# 责任链模式

### 模式
事件的创造者与事件的处理者解耦, 事件的创建方无需关注事件后续如何或是由谁处理

### 简单示例
```python
class NullHandler(object):
    def __init__(self, successor=None):
        self.__successor = successor

    def handle(self, event):
        if self.__successor is not None:
            self.__successor.handle(event)


class AHandler(NullHandler):
    def handle(self, event):
        if event == 'A':
            print "EVENT A"
        else:
            super(AHandler, self).handle(event)


class BHandler(NullHandler):
    def handle(self, event):
        if event == 'B':
            print "EVENT B"
        else:
            super(BHandler, self).handle(event)


class CHandler(NullHandler):
    def handle(self, event):
        if event == 'C':
            print "EVENT C"
        else:
            super(CHandler, self).handle(event)


def main():
    import random
    handler = CHandler(BHandler(AHandler(NullHandler())))
    for i in range(10):
        handler.handle(random.choice(['A', 'B', 'C']))
```

更加 pythonic 的做法是:

```python
import functools

def coroutine(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        generator = function(*args, **kwargs)
        next(generator)
        return generator
    return wrapper
    
@coroutine
def a_handler(successor=None):
    while True:
        event = (yield)
        if event == 'A':
            print 'EVENT A'
        elif successor is not None:
            successor.send(event)


@coroutine
def b_handler(successor=None):
    while True:
        event = (yield)
        if event == 'B':
            print 'EVENT B'
        elif successor is not None:
            successor.send(event)


@coroutine
def c_handler(successor=None):
    while True:
        event = (yield)
        if event == 'C':
            print 'EVENT C'
        elif successor is not None:
            successor.send(event)

def main():
    pipeline = a_handler(b_handler(c_handler()))
    events = [2, 5, 14, 22, 18, 3, 35, 27, 20]
    for i in range(10):
        handler.handle(random.choice(['A', 'B', 'C']))
```

### 实际应用场景
在一个预警系统中, 我们通常需要将不同系统产生的日志进行收集汇总并产生报警, 此时便可以利用责任链把收集系统/分析系统, 以及不同的关联分析引擎之间隔离解耦。例如下面的系统安全事态监控:

首先构造分析引擎基类:

```python
import threading

class Engine(threading.Thread):                         # 继承自线程类, 每个分析引擎对应一个分析线程
    __watchers__ = {}

    def watcher(self, name):
        return self.__watchers__.get(name)

    def __init__(self, name=None, successor=None):
        import Queue
        self.successor = successor
        self.queue = Queue.Queue()
        self.wname = name or self.__class__.__name__
        self.__watchers__[self.wname] = self
        super(Engine, self).__init__(name=self.wname)
        self.setDaemon(True)

    def put(self, event):
        self.queue.put(event)
        if self.successor:
            self.successor.put(event)

    def handle(self, event):                           # 事件处理函数, 用于继承重载
        pass

    def run(self):
        import logging

        if self.successor:
            self.successor.start()

        while True:
            event = self.queue.get()
            try:
                self.handle(event)
            except Exception, e:
                logging.warn('Error: %s %s %s' % (self.wname, event, e))

    def alert(self, ttype, *args, **kwargs):
        if ttype.lower() == 'mail':
            print 'ALERT: mail(%s, %s)' % (args, kwargs)
        if ttype.lower() == 'message':
            print 'ALERT: message(%s, %s)' % (args, kwargs)
        if ttype.lower() == 'phone':
            print 'ALERT: phone(%s, %s)' % (args, kwargs)
```

时间维度上的分析引擎，当某段时间内频繁发生管理员账户登录失败事件时，产生告警：

```python
class SEQEngine(Engine):
    def __init__(self, successor=None):
        from collections import deque
        super(SEQEngine, self).__init__(successor=successor)
        self.data = deque(maxlen=10000)

    def delta(self, times):
        if len(self.data) < times:
            return None
        return self.data[-1]['time'] - self.data[-times]['time']

    def alert(self, ttype, *args, **kwargs):
        super(SEQEngine, self).alert(ttype, 'root login failed too much', *args, **kwargs)

    def handle(self, event):
        if event['data'] == 'ROOT LOGIN FAILED':
            self.data.append(event)
        else:
            return

        delta = self.delta(3)
        if delta and delta < 120:
            self.alert('mail', delta, email='test@mail.com')
        delta = self.delta(5)
        if delta and delta < 120:
            self.alert('message', delta, phone='13500000000')
        delta = self.delta(10)
        if delta and delta < 120:
            self.alert('phone', delta, phone='13500000000')
```

补丁关联引擎，当系统中存在对某已存在漏洞的攻击时，产生告警：

```python
class EventEngine(Engine):
    def __init__(self, successor=None):
        super(EventEngine, self).__init__(successor=successor)
        self.data = {'BUG': set(), 'PATCH': set()}

    def alert(self, ttype, *args, **kwargs):
        print self.data
        super(EventEngine, self).alert(ttype, 'ATTACKED', *args, **kwargs)

    def handle(self, event):
        if ':' not in event['data']:
            return
        ttype, data = event['data'].split(':', 1)
        data = data.strip()
        if ttype in self.data:
            if data not in self.data[ttype]:
                self.data[ttype].add(data)

        if ttype == 'ATTACK':
            if data not in self.data['PATCH']:
                self.alert('mail', data, email='test@mail.com')
            if data in self.data['BUG'] and data not in self.data['PATCH']:
                self.alert('phone', data, phone='13500000000')
```

测试：

```python
def mkevent():
    import time
    import random
    if random.random() > 0.99:
        return {'data': 'ROOT LOGIN FAILED', 'time': time.time()}
    else:
        ttype = random.choice(['BUG', 'ATTACK', 'PATCH'])
        data = random.choice(['A', 'B', 'C', 'D', 'E'])
        return {'data': '%s: %s' % (ttype, data), 'time': time.time()}

if __name__ == '__main__':
    import time

    e = SEQEngine(successor=EventEngine())
    e.start()

    while True:
        e.put(mkevent())
        time.sleep(0.5)
```
