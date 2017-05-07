# 装饰模式
### 模式
装饰模式是在不破坏原有函数处理逻辑的前提下，使用一些方法在外部对函数进行一定扩充。


### 简单示例
A 为原类， Proxy 代理 A，在 operate 函数中调用了 A 的 operate。

```python
def operate(self):
    print 'operate'

def decorate(func):
    def _func(*args, **kwargs):
        print 'haha'
        ret = func(*args, **kwargs)
        print 'hehe'
        return ret
    return _func
    
operate = decorate(operate)
operate()
```
在 python 中，已经有原生语法糖符号`@`封装了`operate = wraps(operate)`这一步，实现了装饰器的构造。如下：

```python
def decorate(func):
    def _func(*args, **kwargs):
        print 'haha'
        ret = func(*args, **kwargs)
        print 'hehe'
        return ret
    return _func

@decorate
def operate(self):
    print 'operate'
operate()
```
但是直接这么装饰以后，你会发现`operate`函数的上下文已经发生了改变，例如`operate.__name__`已经不是 operate 了，所以 python 的`functools.wraps`函数封装了对原有函数上下文的切换：

```python
import functools

def decorate(func):
    @functools. wraps(func)
    def _func(*args, **kwargs):
        print 'haha'
        ret = func(*args, **kwargs)
        print 'hehe'
        return ret
    return _func

@decorate
def operate(self):
    print 'operate'
operate()
```

### 实际应用场景
装饰模式使用起来比较灵活，适用的场景非常丰富，例如 [python-agent](../python-agent/quickstart.md) 框架中，Sender 类对 Output 类的修饰；又如 python 库 toolz 中的一些函数：

```
toolz.memorize   为函数提供缓存功能
toolz.curry      将函数装饰成生产偏函数的装饰器
...
```

在 Web Service 中，为了统一处理异常，返回恰当的 HTTP 码，通常也会使用一层装饰器。

```python
def handler_exc(func):
    @functools. wraps(func)
    def _func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotFoundException:
            return 'Not Found', 404
        except ForbiddenException:
            return 'Forbidden', 403
        except AuthorityException:
            return 'No Authority', 401
    return _func
```
