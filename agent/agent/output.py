#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import gzip
import base64
import StringIO

from . import __version__
from ..logger import Logging
from exception import OutputError

__author__ = 'tong'

logger = Logging()


class Kafka(object):
    def __init__(self, topic, server, client=None, **kwargs):
        try:
            import kafka
        except ImportError:
            raise OutputError('Lack of kafka module, try to execute `pip install kafka-python>=1.3.1` install it')

        client = client or kafka.SimpleClient
        self._producer = None
        self._topic = topic
        try:
            self._kafka = client(server, **kwargs)
        except Exception, e:
            raise OutputError('kafka client init failed: %s' % e)
        self.producer(kafka.SimpleProducer)

    def producer(self, producer, **kwargs):
        try:
            self._producer = producer(self._kafka, **kwargs)
        except Exception, e:
            raise OutputError('kafka producer init failed: %s' % e)

    def send(self, event):
        if not self._producer:
            raise OutputError('No producer init')
        logger.info('OUTPUT INSERT Kafka 1: %s' % self._producer.send_messages(self._topic, event.data))

    def sendmany(self, events):
        if not self._producer:
            raise OutputError('No producer init')
        logger.info('OUTPUT INSERT Kafka %s: %s' %
                    (len(events), self._producer.send_messages(self._topic, *[e.data for e in events])))

    def close(self):
        if self._producer:
            del self._producer
            self._producer = None


class HTTPRequest(object):
    def __init__(self, server, headers=None, method='GET'):
        self.server = server
        self.method = method.upper()
        self.headers = headers or {}
        self.headers.setdefault('User-Agent', 'python-Agent %s HTTPRequest' % __version__)

    def send(self, event):
        import requests
        if self.method == 'GET':
            ret = requests.get(self.server, params=event.raw_data, headers=self.headers)
            logger.info('OUTPUT INSERT Request 1: %s' % ret)
        elif self.method == 'POST':
            ret = requests.post(self.server, data=self.data(event.raw_data), headers=self.headers)
            logger.info('OUTPUT INSERT Request 1: %s' % ret)

    def sendmany(self, events):
        import requests
        data = {'data': self.package(events), 'gzip': '1'}
        if self.method == 'GET':
            ret = requests.post(self.server, params=data, headers=self.headers)
            logger.info('OUTPUT INSERT Request %s: %s' % (len(events), ret))
        elif self.method == 'POST':
            ret = requests.post(self.server, data=self.data(data), headers=self.headers)
            logger.info('OUTPUT INSERT Request %s: %s' % (len(events), ret))

    def data(self, data):
        ctype = self.headers.get('Content-Type')
        if ctype == 'application/json':
            return json.dumps(data, separators=(',', ':'))
        return data

    @staticmethod
    def package(events):
        import urllib

        data = json.dumps([item.raw_data for item in events])
        if isinstance(data, unicode):
            data = data.encode('utf8')

        buf = StringIO.StringIO()
        fd = gzip.GzipFile(fileobj=buf, mode="w")
        fd.write(data)
        fd.close()
        result = buf.getvalue()
        result = base64.b64encode(result)
        result = urllib.urlencode(result).encode('utf8')
        return result


class Csv(object):
    def __init__(self, filename, fieldnames, **kwargs):
        from csv import DictWriter
        self.fp = open(filename, 'w')
        self.filename = filename
        self.fieldnames = fieldnames
        self.kwargs = kwargs
        self.writer = DictWriter(self.fp, fieldnames, **kwargs)
        self.writer.writeheader()

    def send(self, event):
        self.writer.writerow(event.raw_data)
        self.fp.flush()
        logger.info('OUTPUT INSERT CSV 1')

    def sendmany(self, events):
        self.writer.writerows([event.raw_data for event in events])
        self.fp.flush()
        logger.info('OUTPUT INSERT CSV %s' % len(events))

    def close(self):
        self.fp.close()

    def archive(self, filename):
        if filename == self.filename:
            raise Exception('archive name is same as old (%s)' % filename)

        from csv import DictWriter
        os.renames(self.filename, filename)
        self.fp.close()
        self.fp = open(self.filename, 'w')
        self.writer = DictWriter(self.fp, self.fieldnames, **self.kwargs)
        self.writer.writeheader()


class SQLAlchemy(object):
    def __init__(self, table, fieldnames, *args, **kwargs):
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
        except ImportError:
            raise OutputError('Lack of kafka module, try to execute `pip install SQLAlchemy` install it')
        self.engine = create_engine(*args, **kwargs)
        self.DB_Session = sessionmaker(bind=self.engine)
        self.quote = kwargs.pop('quote', '`')
        self._session = None
        self._timer = None
        self._table = table

        action = 'INSERT INTO'
        keys = ','.join(['%s%s%s' % (self.quote, key, self.quote) for key in fieldnames])
        values = ','.join([':%s' % key for key in fieldnames])
        self.fields = fieldnames
        self.sql = '%s %s (%s) VALUES (%s)' % (action, self.table, keys, values)

    @property
    def session(self):
        try:
            if not self._session:
                self._timer = time.time()
                self._session = self.DB_Session()
            elif time.time() - self._timer > 900:
                self._session.close()
                self._session = self.DB_Session()
                self._timer = time.time()
        except:
            self._timer = time.time()
            self._session = self.DB_Session()
        return self._session

    @property
    def table(self):
        return '%s%s%s' % (self.quote, self._table, self.quote)

    def send(self, event):
        data = event.raw_data
        self.session.execute(self.sql, data)
        self.session.commit()

    def sendmany(self, events):
        self.session.execute(self.sql, [event.raw_data for event in events])
        self.session.commit()


class Screen(object):
    def __init__(self, *args, **kwargs):
        self.counter = 0
        self.args = args
        self.kwargs = kwargs

    def __getattr__(self, item):
        return lambda *args, **kwargs: item

    def send(self, event):
        self.counter += 1
        print '=== %s ===' % self.counter
        print 'Type: %s' % event.type
        if isinstance(event.raw_data, basestring):
            print 'Result: %s' % event.raw_data.strip()
        else:
            for key, value in event.raw_data.items():
                print '%s: %s' % (key, value)
        print

    def sendmany(self, events):
        for event in events:
            print self.send(event)


class Null(object):
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, item):
        return lambda *args, **kwargs: item

    def send(self, event):
        pass

    def sendmany(self, events):
        pass
