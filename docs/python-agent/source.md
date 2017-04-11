#  数据源－Source

### 说明
数据源模块, 所有数据源均使用slaver接口得到一个生成器, 并进行后续清洗或是解析操作, 目前支持以下几种数据源。

#### 1、Log
-----------
日志数据源会监听日志文件的行为变化, 实时读取日志文件末尾追加的数据, 并对日志文件的切割归档操作予以判断。

参数：
> `path`: 日志文件路径
> 
> `wait`: 当读取不到新的数据时休眠的时间间隔, 单位为秒, 默认为`3`
>
> `times`: 检查文件切割情况的频率情况, 值越大频率越小, 默认为`3`

示例：

```python
from agent import source
source.Log('/var/log/messages')      # 数据源为/var/log/messages
source.Log('/var/log/messages', wait=10, times=1)
source.Log('/var/log/messages', times=5)

for line in Log('/var/log/messages').slaver():
    print line
```

#### 2、File
------------
与Log类似, 均为文件型数据源， 该类型主要应用于多文件类型或是有趋于稳定特性的文件类型。

多文件主要是指可以使用通配符来适配的一类文件， 如： /tmp/a\*.csv, /nginx/access?.log\*等。

有趋于稳定特性的文件类型主要指不再发生变动，或是scp/cp/mv等其他类似命令产生的正在复制过程中可能会有段时间变化的文件。

参数：
> `path`: 日志文件路径，支持通配符。
> 
> `confirmwait`: 确认文件时间，当文件confirmwait秒内不再发生变化时便确认该文件不再发生变化，开始读取下个文件，单位为秒，默认不等待。
>
> `filewait`: 当没有符合通配符的文件时，等待时间长度，该值为None时不会进行任何等待，数据源读取直接结束。默认为`None`。
> 
> `cachefile`: 文件去重的缓存持久化文件。使用布隆过滤器记录了已经读取过的文件，为None时仅在内存中作去重，不对缓存作持久化。默认为`None`。

示例：

```python
from agent import source
source.File('/var/log/messages')      # 数据源为/var/log/messages
source.File('/var/log/*.log')

for line in File('/var/log/message*'):
    print line
    
for line in File('/var/log/message*', confirmwait=3).slaver():
    print line
    
for line in File('/var/log/message*', filewait=3).slaver():
    print line
```

#### 3、Csv
-----------
与File用法一致，主要正对csv文件进行的优化，当读取的文件类型为csv类型时，建议使用该类型。

参数：
> `path`: 日志文件路径，支持通配符。
> 
> `confirmwait`: 确认文件时间，当文件confirmwait秒内不再发生变化时便确认该文件不再发生变化，开始读取下个文件，单位为秒，默认不等待。
>
> `filewait`: 当没有符合通配符的文件时，等待时间长度，该值为None时不会进行任何等待，数据源读取直接结束。默认为`None`。
> 
> `cachefile`: 文件去重的缓存持久化文件。使用布隆过滤器记录了已经读取过的文件，为None时仅在内存中作去重，不对缓存作持久化。默认为`None`。
>
> `**kwargs`: csv配置参数, 包含分隔符,引用符等, 参照 [csv-reader](https://docs.python.org/2/library/csv.html#reader-objects)

示例：参照File类型数据源。

#### 4、Kafka
-------------
使用Kafka消费者作为数据源。

参数：
> `topic`: kafka主题。
> 
> `servers`: kafka服务器地址。
> 
> `**kwargs`: 其他参数参考 [KafkaConsumer](http://kafka-python.readthedocs.io/en/master/apidoc/KafkaConsumer.html)

示例：

```python
from agent import source
source.Kafka('my-topic', ['localhost:9092'])
source.Kafka('my-topic', group_id='my-group', servers=['localhost:9092'])
```

#### 5、SpeedTest
-----------------
测速源。该数据源并不是一个实体的数据源，嗯，更准确的来讲它应该是个数据源的装饰器。用以测试数据传输以及清洗解析的效率。目前测试结果只能输出到终端，后续可能考虑会加把结果重定向的参数。

参数：
> `source`: 其他数据源对象。

示例：

```python
from agent import source, output, Agent
s = source.Log('/var/log/nginx/access.log')
s = source.SpeedTest(s)
o = output.Null()
a = Agent(s, o, rule=rule('nginx'))
a.start()
```