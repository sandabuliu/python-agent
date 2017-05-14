# 解析模块

本篇纪录 NGINX 日志处理的几种方案。

### 方案一
#### NGINX + LUA

<img src=../../static/nginx-lua.png width=500 />

    1、线上请求打向nginx后，使用lua完成日志整理:如统一日志格式，过滤无效请求，分组等。      
    2、根据不同业务的nginx日志,划分不同的topic
    3、lua实现producter异步发送到kafka集群
    4、对不同日志感兴趣的业务组实时消费获取日志数据
    
优点：实时性强，磁盘冲击小

缺点：请求量暴涨时，给服务端造成的压力大，扩展性较差
    
详细的安装配置步骤可参考 [网站统计中的数据收集原理及实现](http://blog.codinglabs.org/articles/how-web-analytics-data-collection-system-work.html)

### 方案二
#### nginx + [python-agent](../python-agent/quickstart.md)

<img src=../../static/nginx-agent.png width=500 />

    1、使用 Nginx 日志作为缓存池
    2、使用 python-agent 解析日志，并异步发送到kafka集群
    3、对不同日志感兴趣的业务组实时消费获取日志数据
    
当使用 POST 请求发送埋点数据时，需要在 Nginx 日志配置中添加`$request_body`参数，并且由于当 Nginx 后端服务架空时，日志里不会主动读取request_body内容，所以一般服务是纯粹的埋点数据接收服务时，需要使用 echo-nginx-module 插件，安装方法：

    1、wget 'http://nginx.org/download/nginx-1.11.2.tar.gz'
    2、wget https://github.com/openresty/echo-nginx-module/archive/master.zip
    3、unzip master.zip && cd echo-nginx-module-master
    4、./configure --prefix=/opt/nginx --add-module=/opt/nginx/echo-nginx-module
    

优点：与已有的业务系统解耦，可伸缩性强

缺点：请求量暴涨时，实时性降低

### 方案三
#### nginx + python-agent + [distributed-agent](https://github.com/sandabuliu/distributed-agent)

方案二中，Nginx以及日志的记录／读取／解析均需要在同一服务器中，因此很不利于架构的扩展，对服务器压力也会很大，所以可以考虑使用`distributed-agent`将解析过程在集群中实现。

<img src=../../static/nginx-distributed-agent.png width=500 />

`distributed-agent`部署：

```
pip install bokeh
pip install distributed
pip install git+https://github.com/sandabuliu/python-agent.git
pip install git+https://github.com/sandabuliu/blaze-agent.git
pip install git+https://github.com/sandabuliu/distributed-agent.git
```

scheduler启动：

```sh
dask-scheduler
```

worker启动：

```sh
dask-worker 127.0.0.1:8786
```

ui界面：http://scheduler-address:8787/