#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

__author__ = 'tong'


class BaseError(Exception):
    def __init__(self, message):
        self.message = message
        frame = sys._getframe(1)
        code = frame.f_code
        self.name = code.co_name
        self.co_filename = code.co_filename
        self.co_firstlineno = code.co_firstlineno

    def __str__(self):
        return '{filename} [{function}: {lineno}] {message}'.format(
            message=self.message,
            function=self.name,
            filename=self.co_filename,
            lineno=self.co_firstlineno
        )


class InterError(BaseError):
    pass


class EventError(BaseError):
    pass


class SenderError(BaseError):
    pass


class AgentError(BaseError):
    pass


class SourceError(BaseError):
    pass


class OutputError(BaseError):
    pass


class RetryAllowedErr(BaseError):
    pass


RetryAllowedErrs = (RetryAllowedErr, )

try:
    import requests
except ImportError, e:
    pass
else:
    RetryAllowedErrs += (requests.ConnectionError, requests.RequestException)

try:
    from kafka.errors import KafkaError
except ImportError, e:
    pass
else:
    RetryAllowedErrs += (KafkaError, )
