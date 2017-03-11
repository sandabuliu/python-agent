#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import uuid
import logging
import logging.config
import multiprocess

from random import randint
from traceback import format_exc

from ..config import ROOT_PATH

__author__ = 'tong'

sys.modules['multiprocessing'] = multiprocess
logging.config.fileConfig(os.path.join(ROOT_PATH, 'logging.conf'))


class Logging(object):
    class Trace(object):
        def __init__(self, level):
            self.level = level
            self.trace_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, "%s_%s" % (time.time(), randint(0, 100000))))

        @property
        def logger(self):
            return logging.getLogger('trace')

        def trace(self, **kwargs):
            if self.level >= self.logger.level:
                msg = '\n%s\n' % '\n'.join(['[%s]\n%s' % (k.strip(), v.strip()) for k, v in kwargs.items()])
                self.logger.info(msg, extra={'trace_id': self.trace_id})

    @property
    def logger(self):
        return logging.getLogger('agent')

    def debug(self, msg, *args, **kwargs):
        trace = Logging.Trace(logging.DEBUG)
        self.logger.debug(msg, *args, extra={'trace_id': trace.trace_id}, **kwargs)
        return trace

    def info(self, msg, *args, **kwargs):
        trace = Logging.Trace(logging.INFO)
        self.logger.info(msg, *args, extra={'trace_id': trace.trace_id}, **kwargs)
        return trace

    def warn(self, msg, *args, **kwargs):
        trace = Logging.Trace(logging.WARN)
        self.logger.warn(msg, *args, extra={'trace_id': trace.trace_id}, **kwargs)
        exc = format_exc()
        if exc and exc.strip() != 'None':
            trace.trace(format_exc=exc)
        return trace

    def error(self, msg, *args, **kwargs):
        trace = Logging.Trace(logging.ERROR)
        self.logger.error(msg, *args, extra={'trace_id': trace.trace_id}, **kwargs)
        exc = format_exc()
        if exc and exc.strip() != 'None':
            trace.trace(format_exc=exc)
        return trace
