#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Queue
import signal
import threading
from functools import wraps
import multiprocess as multiprocessing

from event import Event
from output import Null
from sender import ctrl_c
from exception import InterError, RetryAllowedErrs

from ..logger import Logging
from ..logparser.exception import ParseException
from ..logparser.logparser import LogParser, ParserResult


__author__ = 'tong'

logger = Logging()


class DefaultParser(object):
    def parse(self, data):
        return ParserResult(data, data, data)


class DefaultCleaner(object):
    def __init__(self, fmt='result'):
        if fmt not in ('result', 'trace'):
            raise Exception('fmt must be "result" or "trace"')
        self.fmt = fmt

    def clean(self, parser):
        if self.fmt == 'result':
            result = parser.result()
        else:
            result = parser.trace()
        if not result:
            logger.debug('BLANK LINE').trace(line=parser.line())
        return result


def send_retry(func, agent):
    @wraps(func)
    def _func(*args, **kwargs):
        err = None
        record = False
        while True:
            try:
                ret = func(*args, **kwargs)
                if record:
                    logger.info('SENDER SENDED')
                return ret
            except Queue.Full:
                if agent.inter.is_set():
                    raise InterError('STOP')
            except RetryAllowedErrs, e:
                if not record or str(err) != str(e):
                    logger.error('SENDER SEND FAILED, RETRY NOW: %s' % e)
                    record = True
                    err = e
                if agent.inter.wait(agent.retry_time):
                    raise InterError('STOP')
    return _func


def try_catch(func):
    @wraps(func)
    def _func(parser):
        try:
            ret = func(parser)
            return ret
        except Exception, e:
            logger.warn('PARSER PASS CLEAN FAILED: %s' % e).trace(
                line=parser.line(), trace=parser.trace(), result=parser.result()
            )
            return None
    return _func


class Agent(multiprocessing.Process):
    def __init__(self, source, sender=None, rule=None, event=Event,
                 clean=None, parser_num=1, queue_size=1024, retry_time=600,
                 process=False, fmt='result', **kwargs):
        if process:
            self.Queue = multiprocessing.Queue
            self.Process = multiprocessing.Process
        else:
            self.Queue = Queue.Queue
            self.Process = threading.Thread

        clean = clean or DefaultCleaner(fmt).clean
        super(Agent, self).__init__(**kwargs)
        self.clean = try_catch(clean)
        self.source = source
        self.sender = sender or Null()
        self.event = event
        self.parser = LogParser(rule) if rule else DefaultParser()
        self.sender.send = send_retry(self.sender.send, self)
        self.qin = self.Queue(queue_size or 1024)
        self.parser_num = 0
        self.parser_init = parser_num or 1
        self.parsers = []
        self.agentname = kwargs.get('name', self.name)
        self.retry_time = retry_time or 600
        self.finish = multiprocessing.Event()
        self.inter = multiprocessing.Event()

    def add_parser(self):
        self.parser_num += 1
        p = self.Process(name='%s-Parser.%s' % (self.agentname, self.parser_num),
                         target=self.process,
                         args=(self.qin, ))
        self.parsers.append(p)
        p.start()
        logger.info('AGENT START PARSER: %s-Parser.%s' % (self.agentname, self.parser_num))

    def operate(self, data):
        try:
            return self.parser.parse(data)
        except ParseException, e:
            logger.warn('PARSER PASS %s Parse error: %s' % (self.agentname, e)).trace(
                line=data.strip(), type=e.type, rule=e.rule, data=e.line
            )
            return None
        except Exception, e:
            logger.warn('PARSER PASS %s Parse unknown error: %s' % (self.agentname, e)).trace(
                line=data.strip(), type=self.parser.rule.type, rule=self.parser.rule.rule
            )
            return None

    def run(self):
        signal.signal(signal.SIGINT, ctrl_c)
        logger.info('AGENT START %s' % self.agentname)
        try:
            slaver = self.source.slaver()
            for i in range(self.parser_init):
                self.add_parser()
        except Exception, e:
            raise logger.error('AGENT INIT %s failed: %s' % (self.agentname, e))

        for data in slaver:
            self.qin.put(data)
        logger.info('AGENT STOPPING %s' % self.agentname)
        self.inter.set()

        for i in range(self.parser_num):
            logger.info('AGENT STOPPING PARSER: %s-Parser.%s' % (self.agentname, i+1))
            self.qin.put(None)
        for p in self.parsers:
            p.join()

        if hasattr(self.sender, 'close'):
            logger.info('AGENT STOPPING %s-Sender' % self.agentname)
            self.sender.close()
        logger.info('AGENT STOP %s' % self.agentname)
        self.finish.set()

    def process(self, qin):
        from multiprocessing import queues
        if isinstance(qin, queues.Queue):
            signal.signal(signal.SIGINT, ctrl_c)
        sender = self.sender
        if hasattr(sender, 'catch'):
            sender.catch(self.agentname)
        while True:
            data = None
            try:
                data = qin.get()
                if data is None:
                    break
                ret = self.operate(data)
                if not ret:
                    continue
                item = self.clean(ret)
                if not item:
                    continue
                sender.send(self.event(item))
            except InterError:
                break
            except BaseException, e:
                logger.warn('PARSER PASS error: %s' % e).trace(line=data)
                continue
        if hasattr(sender, 'throw'):
            sender.throw()
        logger.info('AGENT STOP PARSER')

    def stop(self, async=False):
        self.source.close()
        if not async:
            self.finish.wait()
