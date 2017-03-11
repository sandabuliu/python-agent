#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

from . import __version__
from ..logger import Logging
from exception import OutputError

__author__ = 'tong'

logger = Logging()


class Kafka(object):
    def __init__(self, server, client=None, **kwargs):
        try:
            import kafka
        except ImportError:
            raise OutputError('Lack of kafka module, try to execute `pip install kafka-python>=1.3.1` install it')

        client = client or kafka.SimpleClient
        self._producer = None
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
        logger.info('OUTPUT INSERT Kafka 1: %s' % self._producer.send_messages(event.type, event.data))

    def sendmany(self, events):
        if not self._producer:
            raise OutputError('No producer init')
        senders = {}
        for event in events:
            tp = event.type
            sender = senders.get(tp, [])
            sender.append(event.data)
            senders[tp] = sender

        for sender, messages in senders.items():
            logger.info('OUTPUT INSERT Kafka %s: %s' % (len(messages),
                                                        self._producer.send_messages(sender, *messages)))

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
            ret = requests.post(self.server, data=self.data(event), headers=self.headers)
            logger.info('OUTPUT INSERT Request 1: %s' % ret)

    def sendmany(self, events):
        import requests
        if self.method == 'GET':
            for event in events:
                self.send(event)
        elif self.method == 'POST':
            ret = requests.post(self.server, data=self.data(events), headers=self.headers)
            logger.info('OUTPUT INSERT Request %s: %s' % (len(events), ret))

    def data(self, data):
        if isinstance(data, list):
            data = [event.raw_data for event in data]
        else:
            data = data.raw_data

        ctype = self.headers.get('Content-Type')
        if ctype == 'application/json':
            return json.dumps(data, separators=(',', ':'))
        return data


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


class Screen(object):
    def __init__(self, *args, **kwargs):
        self.counter = 0
        self.args = args
        self.kwargs = kwargs

    def __getattr__(self, item):
        return lambda *args, **kwargs: item

    def send(self, event):
        self.counter += 1
        print str(event)
        print 'Number.%s' % self.counter

    def sendmany(self, events):
        for event in events:
            print event
        self.counter += len(events)
        print 'Number.%s' % self.counter


class Null(object):
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, item):
        return lambda *args, **kwargs: item

    def send(self, event):
        pass

    def sendmany(self, events):
        pass
