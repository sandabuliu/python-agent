# 使用 blaze+python-agent 分析日志

### 准备工作

安装 blaze+python-agent 库

```shell
pip install blaze
pip install git+https://github.com/sandabuliu/python-agent.git
```

### 直接加载日志并分析

```
from blaze import data, resource
from agent import rule, source, Agent

@resource.register('agent:.+')
def resource(uri, **kwargs):
    a = [i for i in Agent(source.File(uri), rule=kwargs.get('rule'))]
    return a

df = data('/Users/tong/test.test', rule=rule('nginx'))    #  df 是一个类似 pandas 中 DataFrame 的对象
print df.peek()
```

关于 python-agent 的详细描述 [python-agent](../python-agent/quickstart.md)

### 实时窗口分析

Todo

### 整合多端日志

Todo