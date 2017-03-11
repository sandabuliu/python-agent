#  Agent


### 安装
-----------
```shell
python setup.py install
```


### QuickStart
---------------
### 示例文件 /tmp/a.csv
```csv
zhangsan, 24, 20100514, "computer sport"
lisi, 26, 20100515, "math english cook"
```

### 使用方法
##### 直接输出
```python
from agent import source, output, Agent
s = source.File('/tmp/a.csv')
o = output.Screen()
a = Agent(s, o)
a.start()
```

##### 解析后输出
```python
from agent import fields, source, output, Agent
names = fields('name', 'age', 'date', 'interesting')
params = {"delimiter":"\t", "quotechar":"\""}
rule = {'type': 'csv', 'rule': params, 'fields': names}
s = source.File('/tmp/a.csv')
o = output.Screen()
a = Agent(s, o, rule=rule)
a.start()
```

##### 使用规则文件存储规则
##### rule1: /tmp/rule1
```config
[person]
type=csv
rule={"delimiter":"\t", "quotechar":"\""}
fields=["name", "age", "date", "interesting"]
```
```python
from agent import rule, source, output, Agent
s = source.File("/tmp/a.csv")
o = output.Screen()
r = rule(rulebase='/tmp/rule1', name='person')
a = Agent(s, o, rule=rule)
a.start()
```

##### rule2: /tmp/rule2 指定数据类型
```config
[person]
type=csv
rule={"delimiter":"\t", "quotechar":"\""}
fields=["name", None, None, "interesting"]
subrules={"age": "person_age", "date": "person_date"}

[person_age]
type=type
rule=number
fields={"age": "0"}

[person_date]
type=type
rule=date
fields={"date": "0"}
```
```python
from agent import rule, source, output, Agent
s = source.File("/tmp/a.csv")
o = output.Screen()
r = rule(rulebase='/tmp/rule2', name='person')
a = Agent(s, o, rule=rule)
a.start()
```