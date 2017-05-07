# 代理模式
### 模式
代理模式使用代理对象根据业务需求来延迟或传递一些操作，通常在 C++ 或 JAVA 中需要代理类与被代理类继承自同一基类，而对于 python 这样的动态语言来说，保持接口统一即可。


### 简单示例
A 为原类， Proxy 代理 A，在 operate 函数中调用了 A 的 operate。

```python
class A(object):
    def operate(self):
        print 'A operate'
        
class Proxy(object):
    def __init__(self):
        self.a = A()
        
    def operate(self):
        self.operate()
        
c = Proxy()
c.operate()
```

### 实际应用场景
一个典型的代理模式的使用场景，在C++中便是智能指针的使用。其它，在远程或与服务的交互操作中也会有所应用。    
例如，当前已经有一个使用长连接方式访问数据库的类 MySQL, 连接在 MySQL 对象初始化时建立，并在对象销毁时断开，如下：

```python
class MySQL(object):
    def __init__(self, host, port, user, passwd):
        self.conn = MySQLdb.connect(
            host=host, port=port, user=user, passwd=passwd
        )
        
    def execute(self, sql):
        return self.conn.execute(sql)
        
    def __del__(self):
        self.conn.close()
```
如果现在需要可以短连数据库，连接随用随连，用完则断的对象，则可以构造一个短连接代理：

```python
class MySQLProxy(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        
    def execute(self, sql):
        conn = MySQL(*self.args, **self. kwargs)
        return conn.execute(sql)
        del conn
        
    def __del__(self):
        pass
```