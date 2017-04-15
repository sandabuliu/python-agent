# 解析规则-rule

### 说明
规则的编写是该框架使用的关键，规则分为自定义规则以及规则库规则。

使用rule函数可读取规则库规则或自定义规则。

### rule函数

> `name`: 规则名称
> 
> `rulebase`: 规则库文件路径。默认为None，使用系统规则库。

### 使用规则库规则

使用`rule`函数读取规则 

```python
from agent import rule, source, output, Agent
s = source.File('/var/log/nginx/access.log')
o = output.Screen()
a = Agent(s, o, rule=rule('nginx'))
a.start()
```

### 使用自定义规则解析
规则：

```config
[person]       # 规则名称
type=csv
rule={"delimiter":"\t","quotechar":"\""}
fields={"0":"name","3":"interesting"}
subrules={"age":"person_age","date":"person_date"}

[person_age]    #子规则名称
type=type
rule=number
fields={"age":"0"}

[person_date]   #子规则名称
type=type
rule=date
fields={"date":"0"}
```
源码：

```python
from agent import rule,source,output,Agent
s = source.File("/tmp/a.csv")
o = output.Screen()
r = rule(rulebase='/tmp/rule', name='person')
a = Agent(s,o,rule=rule)
a.start()
```

### 规则编写

规则编写的主要格式如下例:

```config
[name]                          #  规则名称
type=regex                      #  使用的解析规则类型
rule=(\w+) (\d+) (.+)           #  对应的解析方式
fields=name,age,skills          #  解析后的字段名
subrules={}                     #  设定子规则
```

规则分别由 type, rule, fields, subrules 四个部分组成。     
type／rule 指定了解析的方式。目前所支持的全部解析类型详见后面。    
示例规则可将文本数据```xiaoli 21 c++,java,python```解析为

```json
{
  "name": "xiaoli",
  "age": "21",
  "skills": "c++,java,python"
}
```

fields／subrules 为可选项。
   
fields 除了```name,age,skills```的指定方式外, 还可以通过 list```["name", "age", "skills"]```或 dict ```{"name":"0","age":"1","skills":"2"}```的方式指定。

subrules 可对解析后的字段进行进一步解析，如下：

```config
[name]
type=regex                     
rule=(\w+) (\d+) (.+)           
fields={"name": "0"}   
subrules={"1": "age_number", "2": "skills_split"}  

[age_number]         #  使用数字类型解析age
type=type
rule=number
fields=age

[skills_split]       #  使用split解析skills
type=split
rule={"separator": ","}
fields=skill_1,skill_2,skill_3          
```

可将文本```xiaoli 21 c++,java,python```解析为

```json
{
  "name": "xiaoli",
  "age": 21,
  "skill_1": "c++",
  "skill_2": "java",
  "skill_3": "python"
}
```

##### 解析规则类型：

| type | rule | 类型 | 示例 | 作用 |
| ---- | ---- | ---- | ---- | ---- |
| `regex` | 正则字符串 | string | `(\w+) (\d+) (.+)`<br>`(?P<name>\w+) (?P<age>\d+) (?P<skills>.+)` | 正则匹配 |
| `split` | `separator`: 分隔符<br>`maxsplit`: 最多分隔次数,可选项 | json | `{"separator": ","}`<br>`{"separator": "###", "maxsplit": 2}` | 按分隔符拆分 |
| `type` | `number`/`date`/`string` | string | `number`<br>`date` | 数据类型转换 |
| `kv` | `separator`: 分隔符<br>`linker`: 等号连接符,默认`=` | json |  `{"separator": "&"}`<br>`{"separator": "&", "linker": "-"}` | key-value拆分 |
| `csv` | `separator`: 分隔符,默认`,`<br>`quotechar`: 引用符,默认`"` <br>`quoting`: 引用方式: 0-最小引用,1-全引用,2-非数值引用,3-不引用,默认`0` | json | `{"separator": " "}`<br>`{"separator": "\t", "quotechar": "\""}` | csv解析 |
| `encode` | `utf8`/`gbk`/`string_escape`/`urlquote`等 | string | `utf8`<br>`gbk` | 编码 |
| `decode` | `utf8`/`gbk`/`string_escape`/`urlquote`等 | string | `utf8`<br>`gbk` | 解码 |
| `startswith` | `suffix`: 字符串<br>`start`: 起始位置,默认从头<br>`end`: 结束位置,默认到尾 | json | `{"suffix": "xiaoli"}` | 是否起始于 |
| `endswith` | `suffix`: 字符串<br>`start`: 起始位置,默认从头<br>`end`: 结束位置,默认到尾 | json | `{"suffix": "python"}` | 是否结束于 |
| `contain` |  `suffix`: 字符串<br>`start`: 起始位置,默认从头<br>`end`: 结束位置,默认到尾 | json | `{"suffix": "c++,java"}` | 是否包含 |


### 规则库操作

```python
from agent import rulebase
rulebase.append('/tmp/rule')  # 将新的规则文件补充到系统规则库, 加入后可以直接通过规则名直接加载规则
rulebase.remove(1)            # 删除编号为1的规则文件
rulebase.all()                # 全部规则文件
```

### 其他操作


```python
from agent import ruletocfg
print ruletocfg(name, rule)   # 获得可存储格式规则
                              # name: 规则名,  rule: 规则，dict类型
```