#  数据发送－Sender

### 说明
这个是对output模块能力的扩充，提供一系列发送装饰器，属于非必要模块。

#### 1、Sender
-----------
该sender装饰后与直接使用output区别不大。

参数：
> `output`: 一个output对象。

示例：

```python
from agent import sender, output
o = output.Kafka('my-topic', ['localhost:9092'])
o = sender.Sender(o)
```

#### 2、BatchSender
------------
该sender装饰后结果会批量发送。

参数：
> `output`: 一个output对象。
> 
> `max_size`: 缓存大小，大于该值后将数据打包发送。默认`500`。
> 
> `queue_size`: 队列大小，队列用于缓存发送数据。该值一般大于max_size，使得异步发送期间，队列里还可以append数据。默认值`2000`。
> 
> `flush_max_time`: 刷新时间长度。等待时间超过该值时，会刷新缓存区。单位为秒，默认值`30`。
> 
> `cachefile`: 发送失败时，会把相关失败信息以及数据写到该文件中。默认为`None`。

示例：

```python
from agent import source, output, sender
s = source.Log('/var/log/messages')
o = output.HTTPRequest('http://127.0.0.1:8080')
o = sender.BatchSender(o)
a = Agent(s, o)
a.start()
```
