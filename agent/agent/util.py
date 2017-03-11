#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

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


def fields(*args, **kwargs):
    if args:
        fields = dict(zip(args, [str(i) for i in range(len(args))]))
        fields.pop(None, None)
        return fields
    else:
        return {k: v for k, v in kwargs.items()}
