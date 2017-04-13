#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import pytz
from datetime import datetime, date, time

__author__ = 'tong'


class Filter(object):
    def __init__(self, cachefile, capacity=1000000, error_rate=0.001):
        self.cachefile = cachefile
        if os.name == 'nt' or not cachefile:
            from pybloom import BloomFilter
            if self.cache():
                with open(cachefile, 'r') as fp:
                    self.filter = BloomFilter.fromfile(fp)
            else:
                self.filter = BloomFilter(capacity=capacity, error_rate=error_rate)
        elif os.name == 'posix':
            from pybloomfilter import BloomFilter
            if self.cache():
                self.filter = BloomFilter.open(self.cachefile)
            else:
                self.filter = BloomFilter(capacity, error_rate, cachefile)

    def __contains__(self, key):
        return key in self.filter

    def add(self, obj):
        self.filter.add(obj)
        if os.name == 'nt':
            with open(self.cachefile, 'w') as fp:
                self.filter.tofile(fp)

    def cache(self):
        return os.path.exists(self.cachefile or '')


class JSONCls(json.JSONEncoder):
    def __init__(self, skipkeys=False, ensure_ascii=False, check_circular=True, allow_nan=True, sort_keys=False,
                 indent=None, separators=None, encoding='', default=None):

        super(JSONCls, self).__init__(skipkeys, ensure_ascii, check_circular, allow_nan, sort_keys, indent, separators,
                                      encoding, default)

    def default(self, obj):
        if isinstance(obj, datetime):
            return '%04d-%02d-%02d %02d:%02d:%02d' % (obj.year, obj.month, obj.day, obj.hour, obj.minute, obj.second)
        if isinstance(obj, date):
            return '%04d-%02d-%02d' % (obj.year, obj.month, obj.day)
        if isinstance(obj, time):
            return obj.strftime('%H:%M:%S')
        else:
            return json.JSONEncoder.default(self, obj)


def fields(*args, **kwargs):
    if args:
        fds = dict(zip(args, [str(i) for i in range(len(args))]))
        fds.pop(None, None)
        return fields
    else:
        return {k: v for k, v in kwargs.items()}


class Field(object):
    def __init__(self, name):
        self.name = name
        self.operator = lambda x, y: x == y
        self.value = None
        self.linker = '='

    def set(self, o, v, l):
        self.operator = o
        self.value = v
        self.linker = l
        return self

    def result(self, data):
        if not isinstance(data, dict):
            raise Exception('data should be a dict')
        return self.operator(data.get(self.name), self.value)

    def __eq__(self, other):
        return self.set(lambda x, y: x == y, other, '==')

    def __ne__(self, other):
        return self.set(lambda x, y: x != y, other, '!=')

    def __lt__(self, other):
        return self.set(lambda x, y: x < y, other, '<')

    def __gt__(self, other):
        return self.set(lambda x, y: x > y, other, '>')

    def __le__(self, other):
        return self.set(lambda x, y: x <= y, other, '<=')

    def __ge__(self, other):
        return self.set(lambda x, y: x >= y, other, '>=')

    def __str__(self):
        return '`%s` %s %s' % (self.name, self.linker, json.dumps(self.value, cls=JSONCls))

    @staticmethod
    def parse(value):
        class FieldDict(object):
            def __init__(self, e):
                self.e = e

            def __getitem__(self, item):
                return self.e.get(item, Field(item))

        env = {
            'Field': Field,
            'And': And,
            'Or': Or,
            'pytz': pytz,
            'datetime': datetime
        }
        result = eval(value, env, FieldDict(env))
        if isinstance(result, (tuple, list)):
            result = And(*result)
        return result


class And(object):
    def __init__(self, *args):
        self.args = args

    def result(self, data):
        return all([v.result(data) for v in self.args])

    def __str__(self):
        return ' And '.join(['(%s)' % i for i in self.args])


class Or(object):
    def __init__(self, *args):
        self.args = args

    def result(self, data):
        return any([v.result(data) for v in self.args])

    def __str__(self):
        return ' Or '.join(['(%s)' % i for i in self.args])