#  数据输出－Output

### 说明
简单的说，就是数据的去向，数据导出去处。

#### 1、Kafka
-----------
作为kafka生产者向kafka中产生数据。由于kafka对这一块的配置较为灵活，出于对整个框架结构的考虑该模块目前没有做到那么灵活，有更高需求的可参见高级用法一节。

参数：
> `topic`: kafka topic。
> 
> `server`: kafka服务器（集群）地址。
>
> `client`: kafka生产者类型，详细参考 [KafkaProducer](http://kafka-python.readthedocs.io/en/master/simple.html#simpleproducer-deprecated)。
> 
> `**kwargs`: kafka client参数，详细参考 [KafkaProducer](http://kafka-python.readthedocs.io/en/master/simple.html#simpleproducer-deprecated)。

示例：

```python
from agent import source, output
s = source.Log('/var/log/messages')
o = output.Kafka('my-topic', ['localhost:9092'])
a = Agent(s, o)
a.start()
```

#### 2、HTTPRequest
------------
使用http请求推送数据结果。

参数：
> `server`: http服务器地址。
> 
> `headers`: http请求头，dict类型，默认为空。
>
> `method`: 使用请求类型，`GET` or `POST`，默认`GET`。

示例：

```python
from agent import source, output
s = source.Log('/var/log/messages')
o = output.HTTPRequest('http://127.0.0.1:8080')
a = Agent(s, o)
a.start()
```

#### 3、Csv
-----------
与File用法一致，主要正对csv文件进行的优化，当读取的文件类型为csv类型时，建议使用该类型。

参数：

> `filename`: 文件名。
> 
> `fieldnames`: 字段名，列表类型。
> 
> `**kwargs`: csv配置参数, 包含分隔符,引用符等, 参照 [csv-writer](https://docs.python.org/2/library/csv.html#writer-objects)

示例：

```python
from agent import source, output
s = source.Log('/var/log/messages')
o = output.csv('a.out', ['message'])
a = Agent(s, o)
a.start()
```

#### 4、SQLAlchemy
------------------
输出到数据库表中。目前该输出还不会主动创建表，需要手动先建表，注意字段一致。

参数：

> `table`: 输出的表名。
> 
> `fieldnames`: 字段名，列表类型。
>  
> `quote`: 转移引用符，例如mysql为`` ` ``。
> 
> `*args, **kwargs`: 数据库连接参数等, 参照 [SQLAlchemy-create_engine](http://docs.sqlalchemy.org/en/latest/core/engines.html?highlight=create_engine)

示例：

```python
from agent import output
output.SQLAlchemy('test_tb', ['test1', 'test2', 'test3'], 'sqlite:////absolute/path/to/foo.db'')
```

#### 5、Screen
-----------------
终端标准输出。一般用于测试。

参数：无

示例：

```python
from agent import output
output.Screen()
```

#### 6、Null
-----------------
空输出。一般用于测试。

参数：无

示例：无