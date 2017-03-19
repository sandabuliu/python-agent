#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import time
import glob
import multiprocess as multiprocessing

from exception import SourceError
from util import Filter
from ..logger import Logging

__author__ = 'tong'

logger = Logging()


class Log(object):
    def __init__(self, path, wait=3, times=3, startline=None):
        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise SourceError('logsource init failed, '
                              'cause: No such file %s' % path)
        self.process = None
        self.path = path
        self.stream = None
        self.pos = 0
        self.count = 0
        self.lineno = 0
        self.wait = wait
        self.times = times
        self.inter = multiprocessing.Event()
        self.startline = startline or 0

    def open(self, filename):
        if self.stream and not self.stream.closed:
            self.stream.close()
        self.stream = open(filename)
        self.pos = self.stream.tell()
        self.lineno = 0

    def slaver(self):
        import psutil
        self.process = psutil.Process()
        self.catch()
        for i in range(self.startline):
            self.stream.readline()
        if self.startline < 0:
            self.stream.seek(0, 2)
        while True:
            if self.inter.is_set():
                break
            self.pos = self.stream.tell()
            line = self.stream.readline()
            if not line:
                self.sleep()
            else:
                self.count = 0
                self.lineno += 1
                yield line

    def sleep(self):
        self.count += 1
        if self.count > self.times:
            self.redirect()
            return
        time.sleep(self.wait)
        self.stream.seek(self.pos)

    def redirect(self):
        self.count = 0
        files = self.process.open_files()
        for fo in files:
            if fo.fd == self.stream.fileno():
                if fo.path == self.path:
                    return
                if not os.path.exists(self.path):
                    logger.info('SOURCE LOG %s does not exist, become: %s' %
                                (self.path, fo.path))
                    return
                logger.info('SOURCE LOG redirect to %s, archive to %s (line count: %s)' %
                            (self.path, fo.path, self.lineno))
                self.open(self.path)
                return
        logger.error('SOURCE LOG fd: %s does not exist? what happened?'
                     % self.stream.fileno())
        self.catch()

    def catch(self):
        logger.info('SOURCE LOG try to catch %s...' % self.path)
        while True:
            if self.inter.is_set():
                break
            if os.path.exists(self.path):
                self.open(self.path)
                logger.info('SOURCE LOG catch %s successful' % self.path)
                break
            time.sleep(self.wait)

    def close(self):
        self.inter.set()


class File(object):
    def __init__(self, path, filewait=None, confirmwait=None, cachefile=None):
        self.path = os.path.abspath(path)
        self.inter = multiprocessing.Event()
        self.filename = None
        self.file_wait = filewait
        self.confirm_wait = confirmwait
        self.lineno = 0
        logger.info('SOURCE FILE FILTER: %s: %s' % (self.path, cachefile))
        self.filter = Filter(cachefile)

    @staticmethod
    def endpoint(fp):
        pos = fp.tell()
        fp.seek(0, 2)
        end = fp.tell()
        fp.seek(pos)
        return end

    def open(self, filename):
        self.filename = filename
        logger.info('SOURCE FILE dumping %s' % filename)
        try:
            return open(filename)
        except Exception, e:
            logger.error('SOURCE FILE open %s failed, cause: %s' % (filename, e))
        return None

    def fetch(self, fp):
        endpos = -1
        self.lineno = 0

        while True:
            pos = fp.tell()
            fp.seek(pos)
            for line in fp:
                if self.inter.is_set():
                    break
                if line[-1] == '\n':
                    self.lineno += 1
                    yield line
                else:
                    endpos = fp.tell()
                    fp.seek(-len(line), 1)
                    break
            if self.inter.is_set():
                break
            if not self.confirm_wait:
                break
            self.inter.wait(self.confirm_wait)
            endpoint = self.endpoint(fp)
            if endpoint <= fp.tell() or endpoint <= endpos:
                break
            if self.inter.is_set():
                break
        fp.close()

    def slaver(self):
        while True:
            if self.inter.is_set():
                break
            files = [_ for _ in glob.glob(self.path)
                     if _ not in self.filter]

            if not files:
                if not self.file_wait:
                    break
                self.inter.wait(self.file_wait)
                continue

            logger.info('SOURCE FILE new file %s' % files)
            for filename in sorted(files):
                fp = self.open(filename)
                if not fp:
                    continue

                try:
                    for line in self.fetch(fp):
                        yield line
                except Exception, e:
                    logger.error('SOURCE FILE dumping %s failed, cause: %s' % (filename, e))
                    try:
                        fp.close()
                    except:
                        pass
                    continue

                if self.inter.is_set():
                    break
                self.filter.add(filename)
                logger.info('SOURCE FILE dumping %s End %s' % (filename, self.lineno))

    def close(self):
        self.inter.set()


class Csv(File):
    def __init__(self, path, filewait=None, confirmwait=None, cachefile=None, **kwargs):
        super(Csv, self).__init__(path, filewait, confirmwait, cachefile)
        self.kwargs = kwargs
        self.data = None

    def write(self, data):
        self.data = data

    def fetch(self, fp):
        reader = csv.reader(fp, **self.kwargs)
        writer = csv.writer(self, **self.kwargs)
        for line in reader:
            if self.inter.is_set():
                break
            self.lineno += 1
            writer.writerow(line)
            yield self.data


class Kafka(object):
    def __init__(self, topic, servers, **kwargs):
        try:
            from kafka import KafkaConsumer
        except ImportError:
            raise SourceError('Lack of kafka module, try to execute `pip install kafka-python>=1.3.1` install it')
        self.consumer = KafkaConsumer(topic, bootstrap_servers=servers, **kwargs)
        self.inter = multiprocessing.Event()
        self.topic = topic
        self.servers = servers
        self.end = '@@@END@@@'

    def slaver(self):
        while True:
            try:
                if self.inter.is_set():
                    break
                for msg in self.consumer:
                    if self.inter.is_set():
                        break
                    if msg.value == self.end:
                        break
                    yield msg.value
            except Exception, e:
                logger.error('SOURCE KAFKA fetch failed: topic: %s, '
                             'err: %s' % (self.topic, e))

    def close(self):
        from kafka import KafkaProducer
        self.inter.set()
        producer = KafkaProducer(bootstrap_servers=self.servers)
        producer.send(self.topic, self.end)
        producer.flush()


class SpeedTest(object):
    def __init__(self, source):
        self.source = source
        self.counter = 0

    def slaver(self):
        slaver = self.source.slaver()
        timer = time.time()
        for line in slaver:
            self.counter += 1
            print 'SPEED:', self.counter/(time.time()-timer)
            yield line

    def close(self):
        self.source.close()
