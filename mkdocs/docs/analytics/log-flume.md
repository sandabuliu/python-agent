# 使用Flume采集

### Flume简介

Flume 是 Cloudera 开发的日志收集系统, 具有分布式、高可用等特点。为大数据等日志采集、汇总和传输提供了一条有效可靠的数据通道。Flume 架构简洁， 并且保证了很高的灵活性以及可扩展性，可在日志系统自行定制各类数据源以及数据接收对象。

Flume 主要由以下几个部件组成：

1、Source：数据源。用于实时的接收与定制不同类型的数据源。例如：命令（tail -f）、TCP流、HTTP等方式获取数据，通常一行对应一条数据。

2、Sink：数据的消费者。接收Source中产生的数据流，并发送至指定位置。例如：HDFS，HBASE等。

3、Channel：一个存储区。作为Source以及Sink间的缓存池，通常可配置选择使用内存或文件。

<img src=../../static/flume-struct.jpg width=500 />

### 与 logstash 的比较

从功能上看，Flume 与 ELK 中的 logstash 都是作为一个配置灵活功能强大的数据管道来使用的。那么，他们之间的区别在哪呢。

首先，logstash相比下更为轻量级，配置简易，上手快，所以对新人来说理解起来更简单，运维成本低。但是Flume中由于Channel模块的可配置性，则在数据传输的过程中，更加显得安全不易丢失数据。

其次，从两个工具的诞生历史来看，logstash是作为ELK套件中的一员，原生态就是为es作铺垫的；另一个则更多的是为HDFS而诞生，因此两个工具的应用场景不言而喻。很多情况下二者甚至需要结合使用，如：

<img src=../../static/flume-logstash.png width=500 />

### Flume 安装与配置

##### 1、安装JDK

```shell
yum install java
```

##### 2、安装 Flume

```shell
wget https://mirrors.cnnic.cn/apache/flume/1.5.0/apache-flume-1.5.0-bin.tar.gz --no-check-certificate
tar -zxvf apache-flume-1.5.0-bin.tar.gz
ln -s apache-flume-1.5.0 flume
```

##### 3、环境变量设置

```shell
export FLUME_HOME=/opt/flume
export FLUME_CONF_DIR=$FLUME_HOME/conf
export PATH=.:$PATH::$FLUME_HOME/bin
```

##### 4、编辑配置文件flume.conf

\# 分别定义一个 source／sink／channel  
a1.sources = r1    
a1.sinks = k1    
a1.channels = c1    

\# 从`tail -f`命令中读取数据   
a1.sources.r1.type = exec    
a1.sources.r1.channels = c1    
a1.sources.r1.command = tail -f /var/log/messages    

\# 定义 channel 参数  
a1.channels.c1.type = memory    
a1.channels.c1.capacity = 1000    
a1.channels.c1.transactionCapacity = 100    

\# 输出到日志  
a1.sinks.k1.channel = c1    
a1.sinks.k1.type = logger    

##### 5、启动 Flume

```shell
bin/flume-ng agent -n a1 -c conf -f conf/flume.conf -Dflume.root.logger=INFO,console
```

### 附：输出到 hdfs 的配置文件

	a1.sources = r1  
	a1.sinks = k1  
	a1.channels = c1  
	
	a1.sources.r1.type = exec  
	a1.sources.r1.channels = c1  
	a1.sources.r1.command = tail -F /var/log/messages  
	
	a1.sinks.k1.type = hdfs  
	a1.sinks.k1.channel = c1  
	a1.sinks.k1.hdfs.useLocalTimeStamp = true  
	a1.sinks.k1.hdfs.path = hdfs://127.0.0.1:8020/test/%Y-%m-%d-%H-%M  
	a1.sinks.k1.hdfs.filePrefix = cmcc  
	a1.sinks.k1.hdfs.minBlockReplicas = 1  
	a1.sinks.k1.hdfs.fileType = DataStream  
	a1.sinks.k1.hdfs.writeFormat = Text  
	a1.sinks.k1.hdfs.rollInterval = 60  
	a1.sinks.k1.hdfs.rollSize = 0  
	a1.sinks.k1.hdfs.rollCount = 0  
	a1.sinks.k1.hdfs.idleTimeout = 0  
	
	a1.channels.c1.type = memory  
	a1.channels.c1.capacity = 1000  
	a1.channels.c1.transactionCapacity = 100  
	
	a1.sources.r1.channels = c1  
	a1.sinks.k1.channel = c1