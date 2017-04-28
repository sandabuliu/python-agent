# 使用 blaze+python-agent 分析日志

### 准备工作

安装 blaze+python-agent 库

```shell
pip install blaze
pip install git+https://github.com/sandabuliu/python-agent.git
```

### 直接加载日志并分析

```python
from blaze import data, resource
from agent import rule, source, Agent

@resource.register('agent:.+')
def resource(uri, **kwargs):
    uri = uri[6:]
    a = [i for i in Agent(source.File(uri), rule=kwargs.get('rule'))]
    return a

df = data('/var/log/nginx/access.log', rule=rule('nginx'))    #  df 是一个类似 pandas 中 DataFrame 的对象
print df.peek()
```

关于 python-agent 的详细描述 [python-agent](../python-agent/quickstart.md)

### 实时窗口分析

安装 blaze-agent 插件
```shell
pip install git+https://github.com/sandabuliu/blaze-agent.git
```

demo:
```python
from agent import rule
from blaze import data, compute, by

df = data('agent:/var/log/nginx/access.log', rule=rule('nginx'))
print df.peek()                                                         #  预览数据
print compute(df.count(), chunks=2, chunksize=2000)                     #  计算两个窗口内的个数, 每个窗口大小为 2000
print compute(df.method.distinct().count(), chunks=1, chunksize=10000)  #  计算一个窗口内的请求方法种类, 每个窗口大小为10000
print compute(df.body_bytes_sent.max())                                 #  计算最大发送包大小
print compute(by(df.remote_addr, count=df.count()))                     #  统计不同IP的访问量 
```

### 整合多端日志

Todo