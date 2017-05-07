# 简单工厂模式
### 模式
使用动态的方法构建对象。

### 简单示例
动态构建 A/B 类。

```python
class A(object):
    def operate(self):
        print 'A operate'
        
class B(object):
    def operate(self):
        print 'B operate'

def factory(name):
    if name == 'A':
        return A()
    if name == 'B':
        return B()
    return None

factory('A').operate()
factory('B').operate()
```

这种的实现风格是偏 C++/JAVA 的, 缺点是每加一个实现, 则都要改动`factory`函数, 但在 python 这种动态语言面前, 这都是可以弥补的:

factory.py    
```python
class A(object):
    def operate(self):
        print 'A operate'
        
class B(object):
    def operate(self):
        print 'B operate'
```

main.py   
```python
import factory
getattr(factory, 'A', None).operate()
getattr(factory, 'B', None).operate()
```


### 实际应用场景
例如某个服务，其部署环境是复杂的，不同环境下所依赖的存储方式可能也不太一样，有数据库的环境下使用数据库存储，没有的话使用文件存储，不具备持久化环境的场景下则将数据直接放在内存中：

```python
class SQLMeta(object):
    def __init__(self):
        self.conn = connect()
        
    def insert(self, name, **kwargs):
        self.conn.execute('insert into %s %s values %s' % (name, tuple(kwargs.keys()), kwargs.values()))
        
    def select(self, name, **kwargs):
        ret = self.conn.execute('select * from %s where %s' % (name, ' AND '.join(['%s="%s"' % (k, v) for k, v in kwargs.items()])))
        return dict(ret)
        
    def __del__(self):
        self.conn.close()
        
class MEMMeta(object):
    def __init__(self):
        self.data = {}
        
    def insert(self, name, **kwargs):
        cache = self.data.get(name, [])
        cache.append((name, kwargs))
        self.context[name] = cache
        
    def select(self, name, **kwargs):
        items = self.data.get(name, [])
        for item in items:
            if all([item.get(k)==v for k, v in kwargs.items()]):
                return item
                
class FILEMeta(object):
    def __init__(self):
        self.fp = open('data', 'a')
        
    def insert(self, name, **kwargs):
        self.fp.seek(0, 2)
        self.fp.write('%s:%s' % (name, json.dumps(kwargs)))
        
    def select(self, name, **kwargs):
        self.fp.seek(0)
        for line in self.fp:
            name, value = line.split(':', 1)
            value = json.dumps(value)
            if all([value.get(k)==v for k, v in kwargs.items()]):
                return value
                
    def __del__(self):
        self.fp.close()
        
def factory(meta):
    return global().get(meta, None)
    
db = factory(m)
```
