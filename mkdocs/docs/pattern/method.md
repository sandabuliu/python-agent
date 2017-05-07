# 工厂方法模式
### 模式
使用工厂类动态构建对象。

### 简单示例
动态构建 A 类与 B 类。

```python
class A(object):
    def operate(self):
        print 'A operate'
        
class B(object):
    def operate(self):
        print 'B operate'
        
class AFactory(object):
    def create(self):
        return A()
        
class BFactory(object):
    def create(self):
        return B()

AFactory().operate()
BFactory().operate()
```

### 实际应用场景
在 [简单工程模式](./factory.md) 的最后示例中，假设该程序中需要两种类型的存储介质，分别用来存储大量级以及小量级的存储：

```python
class Factory(object):
    def create(self):
        return factory(self.meta)

class LargeFactory(Factory):
    def __init__(self):
        self.meta = LARGE_META
        
class SmallFactory(Factory):
    def __init__(self):
        self.meta = SMALL_META
```
由于其它模块在使用存储介质的时候使用的`LargeFactory`和`SmallFactory`构造，因此只需修改`LARGE_META`以及`SMALL_META`配置即可。
