from ipserver.core.object_factory import ObjectFactory
from ipserver.core.pipeline import Pipeline
from ipserver.service.http_server import HTTPHandler
from ipserver.ipserver_cmd import IpServerCmd
import re

'''
Customize HTTP handler.

$ python3 customize_http_handler.py --info
$ curl http://localhost:8000
'''


class MyPipeline(Pipeline):
    def pre_configure(self, args):
        args.mode = 'HTTP'
        args.http_opt = 'PASS'

    def post_receive(self, conn_sock, binary):
        return binary

    def pre_send(self, conn_sock, binary):
        return binary


class MyHTTPHandler(HTTPHandler):
    def _respond_content(self, httpio):
        body = '''
<html>
<head><title>Customize HTTP handler</title></head>
<body>
<h1>Customize HTTP handler</h1>
<div>
<h2>Request headers</h2>
<pre>
{}
</pre>
</div>
</body>
</html>
'''.format(self.headers)

        httpio.body = body

        super()._respond_content(httpio)


class MyObjectFactory(ObjectFactory):
    def create_pipeline(self):
        return MyPipeline()

    def create_http_handler(self, conn_sock, port, pipeline, args, shared_object):
        return MyHTTPHandler(conn_sock, port, args, shared_object)


if __name__ == '__main__':
    factory = MyObjectFactory()

    cmd = IpServerCmd(factory)

    cmd.run()
