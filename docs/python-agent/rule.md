# 解析规则-rule

### 说明
规则的编写是该框架使用的关键，规则分为自定义规则以及规则库规则。

使用rule函数可读取规则库规则或自定义规则。

### rule函数

> `name`: 规则名称
> 
> `rulebase`: 规则库文件路径。默认为None，使用系统规则库。

### 使用规则库规则

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

TODO

### 规则库操作

```python
from agent import rulebase
rulebase.append('/tmp/rule')  # 使用规则文件扩充规则库
rulebase.remove(1)            # 删除编号为1的规则文件
rulebase.all()                # 全部规则文件
```

### 其他操作


```python
from agent import ruletocfg
print ruletocfg(name, rule)   # 获得可存储格式规则
                              # name: 规则名,  rule: 规则，dict类型
```