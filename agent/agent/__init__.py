#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

__author__ = 'tong'
__version__ = '1.0.0'


def py_encode_basestring_ascii_improved(s):
    """Return an ASCII-only JSON representation of a Python string
    """
    if json.encoder.c_encode_basestring_ascii:
        try:
            return json.encoder.c_encode_basestring_ascii(s)
        except:
            pass

    if isinstance(s, str) and json.encoder.HAS_UTF8.search(s) is not None:
        for coding in ('utf-8', 'gbk'):
            try:
                s = s.decode(coding)
                break
            except:
                pass
        else:
            try:
                s = '<Unknown Encoding>%s' % s.encode('string_escape')
            except:
                s = '<Unknown Encoding>'

    def replace(match):
        s = match.group(0)
        try:
            return json.encoder.ESCAPE_DCT[s]
        except KeyError:
            n = ord(s)
            if n < 0x10000:
                return '\\u{0:04x}'.format(n)
            else:
                # surrogate pair
                n -= 0x10000
                s1 = 0xd800 | ((n >> 10) & 0x3ff)
                s2 = 0xdc00 | (n & 0x3ff)
                return '\\u{0:04x}\\u{1:04x}'.format(s1, s2)
    return '"' + str(json.encoder.ESCAPE_ASCII.sub(replace, s)) + '"'

json.encoder.encode_basestring_ascii = py_encode_basestring_ascii_improved
