#  Agent

### 说明
这是一个数据结构化框架, 可用作数据清洗, 数据结构化预处理, 数据管道等应用场景

### 流程 & 结构
-----------
<img src=mkdocs/docs/static/structure.png />


### 安装
-----------
```shell
pip install git+https://github.com/sandabuliu/python-agent.git
```
or

```shell
git clone https://github.com/sandabuliu/python-agent.git
cd python-agent
python setup.py install
```


### QuickStart
---------------
### Nginx日志
```txt
52.53.224.247 - - [14/Dec/2016:14:35:08 +0000] "POST / HTTP/1.1" 400 0 "-" "User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)" "-"
123.125.71.76 - - [18/Mar/2017:09:50:34 +0000] "GET / HTTP/1.1" 200 5981 "-" "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)" "-"
...
```

### 使用方法
##### 直接输出
```python
from agent import source, output, Agent
s = source.File('/var/log/nginx/access.log')
o = output.Screen()
a = Agent(s, o)
a.start()
```

输出结果:

	=== 1 ===
	Type: default
	Result: 52.53.224.247 - - [14/Dec/2016:14:35:08 +0000] "POST / HTTP/1.1" 400 0 "-" "User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)" "-"

	=== 2 ===
	Type: default
	Result: 123.125.71.76 - - [18/Mar/2017:09:50:34 +0000] "GET / HTTP/1.1" 200 5981 "-" "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)" "-"

	...

##### 使用nginx规则解析输出
```python
from agent import rule, source, output, Agent
s = source.File('/var/log/nginx/access.log')
o = output.Screen()
a = Agent(s, o, rule=rule('nginx'))
a.start()
```

输出结果：

	=== 1 ===
	Type: default
	status: 400
	body_bytes_sent: 0
	remote_user: -
	http_referer: -
	remote_addr: 52.53.224.247
	request: POST / HTTP/1.1
	version: HTTP/1.1
	http_user_agent: User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)
	time_local: 2016-12-14 14:35:08
	path: /
	method: POST
	
	=== 2 ===
	Type: default
	status: 200
	body_bytes_sent: 5981
	remote_user: -
	http_referer: -
	remote_addr: 123.125.71.76
	request: GET / HTTP/1.1
	version: HTTP/1.1
	http_user_agent: Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)
	time_local: 2017-03-18 09:50:34
	path: /
	method: GET

	...
	
详细内容, 见: [http://t.navan.cc](http://t.navan.cc/python-agent/quickstart/)

Copyright © 2017 [g_tongbin@foxmail.com](mailto:g_tongbin@foxmail.com)