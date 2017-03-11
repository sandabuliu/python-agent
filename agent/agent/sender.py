#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import uuid
import time
import signal
import threading
from random import randint
import multiprocess as multiprocessing
from Queue import Queue
from exception import RetryAllowedErrs
from ..logger import Logging

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

    def catch(self, name):
        self.name = name

    def throw(self):
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

    def catch(self, name):
        super(BatchSender, self).catch(name)
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


class AsyncBatchSender(Sender):
    class AsyncFlush(multiprocessing.Process):
        def __init__(self, sender):
            super(AsyncBatchSender.AsyncFlush, self).__init__(name='AsyncSender')
            self._sender = sender
            self._stop_event = multiprocessing.Event()
            self._finished_event = multiprocessing.Event()

        def stop(self):
            self._stop_event.set()
            self._finished_event.wait()
            logger.info('SENDER ASYNCSENDER STOP')

        def run(self):
            err = None
            record = False
            signal.signal(signal.SIGINT, ctrl_c)
            while True:
                try:
                    self._sender.need_flush.wait(self._sender.flush_max_time)
                    if self._sender.push():
                        self._sender.need_flush.clear()
                    if self._stop_event.is_set():
                        break
                    if record:
                        logger.info('SENDER SENDED')
                        record = False
                        err = None
                except Exception, e:
                    if not record or err != e:
                        logger.error('SENDER SEND FAILED, RETRY NOW: %s' % e)
                        record = True
                        err = e
            self._finished_event.set()

    def __init__(self, output, flush_max_time=3, flush_size=100, max_batch_size=500, max_size=2000):
        super(AsyncBatchSender, self).__init__(output)
        self._flush_size = flush_size
        self.flush_max_time = flush_max_time
        self._max_batch_size = max_batch_size
        self._max_size = max_size

        self._buffers = []
        self._queue = multiprocessing.Queue(self._max_size)
        self.need_flush = multiprocessing.Event()
        self._flushing = AsyncBatchSender.AsyncFlush(self)
        self._flushing.daemon = True
        self._flushing.start()

    def send(self, event):
        self._queue.put(event)
        if self._queue.qsize() >= self._flush_size:
            self.need_flush.set()

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

        if len(self._buffers) > 0:
            if hasattr(self._output, 'sendmany'):
                self._output.sendmany(self._buffers)
            else:
                for event in self._buffers:
                    self._output.send(event)
            ret = True
            self._buffers = []

        if self._queue.qsize() < self._flush_size:
            ret = True
        return ret

    def close(self):
        self._flushing.stop()
        while not self._queue.empty() or self._buffers:
            self.push()
        super(AsyncBatchSender, self).close()
