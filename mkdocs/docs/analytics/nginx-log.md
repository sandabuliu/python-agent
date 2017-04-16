##### Nginx 作为一般web程序的入口，其日志通常可用作一些流量统计分析的数据来源，其可配置的字段含义如下：

| 参数 | 说明 | 示例 |
| ---- | ---- | ---- | 
| `$remote_addr` |	客户端IP地址 | 211.28.65.253 |
| `$remote_user` | 客户端用户名称	| - | 
| `$time_local`	 | 访问时间和时区	| 18/Jul/2012:17:00:01 +0800 |
| `$request` | 	请求的URI和HTTP协议	| "GET /article-10000.html HTTP/1.1" |
| `$http_host` | 请求地址，即浏览器中你输入的地址（IP或域名）	| www.it300.com<br>192.168.100.100 |
| `$status` | 	HTTP请求状态	| 200 |
| `$upstream_status` | upstream状态	| 200 |
| `$body_bytes_sent` | 发送给客户端文件内容大小	| 1547 |
| `$http_referer` | 	url跳转来源		| https://www.baidu.com/ |
| `$http_user_agent` | 	用户终端浏览器等信息	| "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SV1; GTB7.0; .NET4.0C; |
| `$ssl_protocol` | 	SSL协议版本		| TLSv1 |
| `$ssl_cipher`		| 交换数据中的算法 | 	RC4-SHA |
| `$upstream_addr` | 	后台upstream的地址，即真正提供服务的主机地址	| 10.10.10.100:80 |
| `$request_time` | 整个请求的总时间, 从第一个字节接收到最后一个字节发出 | 0.205 |
| `$upstream_response_time` | 从Nginx向后端建立连接开始到接受完数据然后关闭连接为止的时间	| 0.002 |
| `$request_body` | POST请求中的body内容，需后台有处理才会记录在日志，在埋点服务器中nginx被用作架空服务时，可使用`echo-nginx-module`或`lua-nginx-module`模块进行处理。| - |
| `$msec` | 日志落盘时间 | 1.205 |
| `$connection` | 连接的序列号 |  |
| `$connection_requests` | 当前通过一个连接获得的请求数量 | 1 |
| `$pipe` | 如果请求是通过HTTP流水线(pipelined)发送，pipe值为“p”，否则为“.” | . |
| `$request_length` | 请求的长度（包括请求行，请求头和请求正文）| 2587 |
| `$time_iso8601` | ISO8601标准格式下的本地时间 |  |
