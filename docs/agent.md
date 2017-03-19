#  数据处理－Agent

### 说明
Agent启动时会产生一个进程，根据配置项进行数据清洗，解析等等操作。

#### 初始化参数

`name`: Agent Name。

`source`: 数据源。一个source对象，详细参考 [数据源-Source](./source.md)

`sender`: 发送器。一个output或sender对象，详细参考 [数据输出-Output](./output.md) or [数据发送-Sender](./sender.md)。默认为`None`，使用Null类型的output。

`rule`: 解析规则，`dict`类型，通常不直接指定而使用rule读取规则文件，详细参考 [解析规则-rule](./rule.md)。

`event`: 事件类，一般用于自定义扩展。详细参考 [高级用法](./high-level.md)。

`clean`: 数据清洗回调函数。默认为`None`。

`parser_num`: 解析器个数。默认为`1`。

`process`: 解析器是否使用进程模式，默认为线程模式。

`queue_size`: 队列大小。该队列用于数据源与解析器间通信。默认为`1024`。

`retry_time`: 当数据发送失败时的重试等待时间。

`fmt`: 解析方式，分为`result`与`trace`两种, 默认为`result`，`trace`一般用于自定义清洗模式。详细参考 [高级用法](./high-level.md)。

#### 接口

	agent.start()             启动一个agent。
	agent.stop(async=False)   停止agent，参数async表示异步停止。
	agent.daemon              异步标记，需要调用start()前配置生效，默认False。
	agent.add_parser()        添加一个解析器。
