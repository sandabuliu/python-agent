#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from exception import EventError

__author__ = 'tong'


class Event(object):
    __TYPE__ = 'default'
    __AUTO_TYPE__ = None

    @classmethod
    def set_type(cls, value=None, autofunc=None):
        if value:
            cls.__TYPE__ = value
        if autofunc:
            cls.__AUTO_TYPE__ = [autofunc]

    def __init__(self, items):
        if not items:
            raise EventError('Event lack of data')
        self._data = None
        self._type = None

        self.data = items
        self.type = self.__TYPE__

        if self.__AUTO_TYPE__:
            try:
                self.type = self.__AUTO_TYPE__[0](items)
            except Exception, e:
                raise Exception('Get auto type failed, cause: %s' % e)

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def data(self):
        return json.dumps(self._data, separators=(',', ':'), sort_keys=True)

    @data.setter
    def data(self, value):
        if not isinstance(value, (dict, tuple, list, basestring, int, float)):
            raise EventError('Event must be json object')
        self._data = value

    @property
    def raw_data(self):
        return self._data

    def __str__(self):
        return '[%s] %s' % (self.type, self.data)
