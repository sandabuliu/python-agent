# 使用FLASK构建REST API

### 前言

简单的用`python`中的`Flask`框架介绍一下 Restful API 的构建。  
  
在`Flask`中，专门用来构建 Restful API 的插件有不少，这里使用`Flask-RESTPlus`作为示例，主要其可以帮助开发自动化生成 Swagger 文档，节省不少开发时间。   

可以通过以下命令进行安装：

```
pip install flask-restplus
```

### 应用

#### 示例

```python
from flask import Flask
from flask_restplus import Resource, Api

app = Flask(__name__)
api = Api(app)

@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

if __name__ == '__main__':
    app.run()
```
HelloWorld 类是 WebService 中处理`/hello`URI 的一个 handler，需要继承自`Resource`类，可以通过重载`get/post/put/delete`等方法进行相应 method 的处理。

程序运行后，可以通过`http://127.0.0.1:5000`访问 API 文档。

#### Api 类
常用的参数：

| 参数 | 说明 |
| --- | --- |
| app | Flask 应用 |
| version | API 版本 |
| title | API 标题 |
| description | API 描述 |
| doc | API 文档访问 URI |
| prefix | API 前缀，默认为`/`, 通常为`/api` |

#### Namespace
使用`api.namespace`构建命名空间。   
 
```python
api = Api(app, prefix='/api')
ns = api.namespace('student', description='TODO operations')

@ns.route('/name')
class Name(Resource):
   ... ...
   
@ns.route('/age')
class Name(Resource):
   ... ...
```

#### 返回值文档
```python
from collections import OrderedDict

from flask import Flask
from flask_restplus import fields, Api, Resource

app = Flask(__name__)
api = Api(app)

model = api.model('Model', {
    'task': fields.String,
    'uri': fields.Url('todo_ep')
})

class TodoDao(object):
    def __init__(self, todo_id, task):
        self.todo_id = todo_id
        self.task = task
        self.status = 'active'

@api.route('/todo')
class Todo(Resource):
    @api.response(404, '找不到该资源')   #  错误码以及错误信息
    @api.marshal_with(model)           #  描述了正常返回值的 JSON 格式
    def get(self, **kwargs):
        return TodoDao(todo_id='my_todo', task='Remember the milk')
```

#### 请求参数
```
from flask_restplus import Api
api = Api(app)

parser = api.parser()
parser.add_argument('name', type=str, required=True, help='test', location='args')

args = parser.parse_args()
```
其中，

    name      参数名    
    type      参数类型  
    required  是否必要参数
    help      参数描述信息
    location  参数位置，包括：
         args     URL 请求参数中
         form     POST 请求 BODY 中，FORM格式
         headers  请求头中
         cookies  放在 cookies 中
         files    上传文件

#### 描述文档
`Flask-RESTPlus`中，添加文档的方式很多，例如`@api.doc`/`@api.marshal_with`/`@api.response`等，也可以直接对函数或类直接编写`__doc__`。但是这些装饰器与全部写在处理函数中，会显得代码比较混乱，也不方便专注的进行逻辑的排查。下面介绍一种将这些文档装饰器与代码逻辑分离的方法：

`APIDoc` 类用于专注生产各种文档对象
 
```python
from toolz import merge
from flask_restplus import fields

SESSION_PUT_RESP = {200: '登陆成功', 400: '认证失败'}

SESSION_POST_MARS = [{'name': 'result', 'type': fields.String, 'desc': '登陆成功', 'example': 'success'}]
SESSION_POST_RESP = merge(SESSION_PUT_RESP, {404: '获取会话失败, 已经在其它地方登陆'})
SESSION_POST_ARGS = [
    ('username', str, True, '用户名', 'form'),
    ('password', str, True, '密码', 'form')
]

SESSION_DEL_MARS = [{'name': 'result', 'type': fields.String, 'desc': '注销成功', 'example': 'success'}]
SESSION_DEL_RESP = {200: '注销成功', 401: '认证失败, 没有登陆'}

class APIDoc(object):
    documents = {
        'session': {
            'desc': '登陆/注销',
            'post': ('登陆', SESSION_POST_MARS, SESSION_POST_RESP, SESSION_POST_ARGS),
            'delete': ('注销', SESSION_DEL_MARS, SESSION_DEL_RESP),
            'put': ('重新登陆', SESSION_POST_MARS, SESSION_PUT_RESP, SESSION_POST_ARGS)
        }
    }

    def __init__(self, ns):
        self.ns = ns

    def marshal_with(self, name, method):
        info = self.documents.get(name, {}).get(method)
        if not info:
            return None
        if not isinstance(info, (list, tuple)):
            return None
        if len(info) < 2:
            return None
        if not info[1]:
            return None
        return self.ns.model(name, {
            m.get('name'): m.get('type')(description=m.get('desc', ''), example=m.get('example', '')) for m in info[1]
        })

    def response(self, name, method):
        info = self.documents.get(name, {}).get(method)
        if not isinstance(info, (list, tuple)):
            return {}
        if not info[2]:
            return {}
        return info[2]

    def arguments(self, name, method):
        info = self.documents.get(name, {}).get(method)
        if not info:
            return None
        if not isinstance(info, (list, tuple)):
            return None
        if len(info) < 4:
            return None
        if not info[3]:
            return None
        parser = self.ns.parser()
        for name, ttype, required, desc, location in info[3]:
            parser.add_argument(name, type=ttype, required=required, help=desc, location=location)
        return parser

    def description(self, *args):
        if not args:
            return ''

        info = self.documents.get(args[0], {})
        if len(args) == 1:
            return info.get('desc') or ''
        if len(args) == 2:
            desc = info.get(args[1]) or ''
            if isinstance(desc, (list, tuple)):
                desc = desc[0]
            else:
                desc = ''
            return desc
        return ''
```

`api_handler` 装饰器用于装饰 HTTP RequestHandler 的类，根据`APIDoc`中的文档情况自动生成文档。

```python
from flask_restplus import Api
from document import APIDoc

app = Flask(__name__)
api = Api(
    app, version='1.0', title='API',
    description='API, 版本 1.0', doc='/doc', prefix='/api'
)

def func_handler(ns, api_cls):
    doc = APIDoc(ns)

    def _handler(func):
        name = api_cls.__name__.lower()
        method = func.__name__
        func.__doc__ = doc.description(name, method)
        func = ns.doc(responses=doc.response(name, method))(func)

        parser = doc.arguments(name, method)
        if parser:
            api_cls.parsers[method] = parser
            func = ns.expect(parser)(func)

        mars = doc.marshal_with(name, method)
        if mars:
            func = ns.marshal_with(mars)(func)
        return func
    return _handler


def api_handler(ns):
    def _handler(api_cls):
        api_cls.parsers = {}
        methods = ['get', 'post', 'put', 'delete']
        for method in methods:
            func = getattr(api_cls, method, None)
            if func:
                func_handler(ns, api_cls)(func.im_func)
        return api_cls
    return _handler
```

登陆逻辑实现

```
from flask_restplus import Resource
from document import APIDoc
from server import api, api_handler

@ns.route('/')
@api_handler(ns)
class Session(Resource):
    def post(self):
        # 登陆逻辑实现
        return {'result': 'success'}

    def put(self):
        # 重新登陆逻辑实现
        return {'result': 'success'}

    def delete(self):
        ＃ 注销逻辑实现
        return {'result': 'success'}
```

这样最后一部分的逻辑实现可以显得很简洁。

#### 官方文档链接
[Flask-RESTPlus](http://flask-restplus.readthedocs.io/en/latest/)