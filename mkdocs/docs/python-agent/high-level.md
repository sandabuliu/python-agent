# 其他补充

### 模块日志

`python-agent`包中内置了两个 logger ——`agent` 和 `trace`。

默认仅添加了一个`NullHandler`， 可通过 python 的日志模块 `logging` 进行配置。具体使用可详见 [logging - Logging facility for Python](https://docs.python.org/2/library/logging.html)。

`agent` 日志中记录了全部解析信息， 其中不同的日志级别记录了不同的日志信息：    

INFO：日志记录了 source，output 等模块的运行时信息。    
WARN：解析错误的日志信息，不影响主程序运行。    
ERROR：各模块中的错误信息。   

`trace` 日志中记录了详细错误信息／traceback／解析错误的规则日志详情等。    
通过一个 uuid 与`agent`中的日志对应。

### 序列化
| 对象 | 读入内存 | 序列化 |
| ---- | ---- | ---- |
| 规则 | `rule` | `ruletocfg` |
| 过滤条件 | `Field.parse` |  |

### 关于 Event

#### Todo

### 关于agent中的clean回调

#### Todo