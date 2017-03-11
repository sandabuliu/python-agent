#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from dateutil.parser import parse
from exception import ParseException

__author__ = 'tong'


class Datatype(object):
    def __init__(self, data):
        self._data = data

    def __str__(self):
        return str(self._data)

    __repr__ = __str__

    @classmethod
    def get(cls, item):
        item = item.lower()
        for subcls in cls.__subclasses__():
            if item == subcls.__name__.lower():
                return subcls
        raise Exception(u'未知类型: %s' % item)


class Number(Datatype):
    pattern = re.compile(r"(\d*\.)?\d+")

    def __init__(self, data):
        data = str(data)
        res = re.match(Number.pattern, data)
        if res:
            data = res.group()
        elif data.lower().startswith('0x'):
            data = int(data, 16)
        else:
            raise ParseException('%s is not a number' % data)
        super(Number, self).__init__(data)


class Date(Datatype):
    def __init__(self, data):
        data = parse(data, fuzzy=True).strftime('%Y-%m-%d %H:%M:%S')
        super(Date, self).__init__(data)


class String(Datatype):
    def __init__(self, data):
        super(String, self).__init__(data)
