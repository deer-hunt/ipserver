from ipserver.core.object_factory import ObjectFactory
from ipserver.core.pipeline import Pipeline
from ipserver.ipserver_cmd import IpServerCmd
from datetime import datetime

'''
Response HTTP by raw data.

$ python3 tcp_raw_http_response.py --port=8002
$ curl http://develop-server:8002/
'''


class MyPipeline(Pipeline):
    def pre_configure(self, args):
        args.mode = 'TCP'

    def complete_receive(self, conn_sock, binary, send_binary=None):
        command = binary.decode().strip()

        response = None

        if command:
            response = self._create_dummy_response()

        return response

    def _create_dummy_response(self):
        content = '''<html>
<head>
<title>Hello! - Raw response</title>
</head>
<body>
<h1>Hello! - Raw response</h1>
<div>
This is raw response.
</div>
<div>
Datetime: {}
</div>
</body>
</html>'''

        now = datetime.now()

        content = content.format(now)

        response = '''HTTP/1.1 200 OK
Date: Sat, 01 Mar 2025 12:00:00 GMT
Server: IpServer
Content-Type: text/html
Content-Length: {}

{}
'''

        response = response.format(len(content), content)

        return response.encode()

    def pre_send(self, conn_sock, binary):
        return binary


class MyObjectFactory(ObjectFactory):
    def create_pipeline(self):
        return MyPipeline()


if __name__ == '__main__':
    factory = MyObjectFactory()

    cmd = IpServerCmd(factory)

    cmd.run()
