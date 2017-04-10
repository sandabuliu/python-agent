#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import uuid
import time
import threading
from random import randint
from Queue import Queue
from exception import RetryAllowedErrs
from ..logger import Logging
from .util import And

__author__ = 'tong'

logger = Logging()


def ctrl_c(signum, frame):
    logger.debug('process ignore ctrl+c')


class Sender(object):
    def __init__(self, output):
        self._output = output
        self.name = None

    @property
    def output(self):
        return self._output

    def catch(self, agent):
        if isinstance(self._output, Sender):
            self._output.catch(agent)
        self.name = agent.agentname
        self.fieldtypes = agent.parser.fieldtypes

    def throw(self):
        if isinstance(self._output, Sender):
            self._output.throw()
        pass

    def send(self, event):
        self._output.send(event)

    def sendmany(self, events):
        self._output.sendmany(events)

    def flush(self):
        pass

    def close(self):
        if hasattr(self._output, 'close'):
            self._output.close()


class BatchSender(Sender):
    class FlushThread(threading.Thread):
        def __init__(self, sender):
            super(BatchSender.FlushThread, self).__init__(name='%s-BatchSender' % sender.name)
            self._sender = sender
            self._stop_event = threading.Event()
            self._finished_event = threading.Event()

        def stop(self):
            self._stop_event.set()
            self._finished_event.wait()

        def run(self):
            err = None
            record = False
            while True:
                try:
                    self._sender.need_flush.wait(self._sender.flush_max_time)
                    if self._sender.push():
                        self._sender.need_flush.clear()
                    if self._stop_event.isSet():
                        logger.info('SENDER STOPPING')
                        break
                    if record:
                        logger.info('SENDER SENDED')
                        record = False
                        err = None
                except RetryAllowedErrs, e:
                    if not record or str(err) != str(e):
                        logger.error('SENDER SEND FAILED, RETRY NOW: %s' % e)
                        record = True
                        err = e
                    if self._stop_event.isSet():
                        break
                except Exception, e:
                    filename = self._sender.save()
                    logger.error('SENDER SEND FAILED, IGNORE NOW: %s, SAVE TO %s' % (e, filename))
            self._finished_event.set()
            logger.info('SENDER STOP')

    def __init__(self, output, max_size=500, queue_size=2000, flush_max_time=30, timeout=2, cachefile=None):
        super(BatchSender, self).__init__(output)
        self._flush_size = int(max_size * 0.8)
        self.flush_max_time = flush_max_time
        self._max_batch_size = max_size
        self._max_size = queue_size
        self._queue = None
        self._timeout = timeout
        self._cache = cachefile

        self.need_flush = None
        self._buffers = None
        self._flushing_thread = None

    def catch(self, agent):
        super(BatchSender, self).catch(agent)
        self._buffers = []
        self._queue = Queue(self._max_size)
        self.need_flush = threading.Event()
        self._flushing_thread = BatchSender.FlushThread(self)
        self._flushing_thread.daemon = True
        self._flushing_thread.start()

    def send(self, event):
        self._queue.put(event)
        if self._queue.qsize() >= self._flush_size:
            self.need_flush.set()

    def sendmany(self, events):
        for event in events:
            self.send(event)

    def flush(self):
        if self.need_flush:
            self.need_flush.set()

    def push(self):
        ret = False
        if not self._buffers:
            for i in range(self._max_batch_size):
                if not self._queue.empty():
                    self._buffers.append(self._queue.get_nowait())
                else:
                    break

        if self._buffers:
            if hasattr(self._output, 'sendmany'):
                self._output.sendmany(self._buffers)
            else:
                for event in self._buffers:
                    self._output.send(event)
            self._buffers = []

        if self._queue.qsize() < self._flush_size:
            ret = True
        return ret

    def save(self):
        buffers = self._buffers
        self._buffers = []
        try:
            filename = str(uuid.uuid3(uuid.NAMESPACE_DNS, "%s_%s" % (time.time(), randint(0, 100000))))
            filename = os.path.join(self._cache, filename)
            fp = open(filename, 'w')
            for event in buffers:
                fp.write(str(event))
            return filename
        except Exception, e:
            return 'Save Failed, cause: %s' % e

    def throw(self):
        self.flush()
        if self._flushing_thread:
            self._flushing_thread.stop()
        while self._queue and not self._queue.empty() or self._buffers:
            try:
                self.push()
            except Exception, e:
                logger.error('SENDER CLEAR ERROR: %s' % e)
                break

    def close(self):
        super(BatchSender, self).close()


class FilterSender(Sender):
    def __init__(self, output, *args):
        super(FilterSender, self).__init__(output)
        self.filter = And(*args)

    def send(self, event):
        if self.filter.result(event.raw_data):
            self.output.send(event)

    def sendmany(self, events):
        for event in events:
            self.send(event)
