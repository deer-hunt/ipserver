from ipserver.core.object_factory import ObjectFactory
from ipserver.core.pipeline import Pipeline
from ipserver.ipserver_cmd import IpServerCmd
from datetime import datetime

import re

'''
URL routing.

Command:
# python3 http_url_routing.py --port=8002
'''


class MyPipeline(Pipeline):
    def pre_configure(self, args, conf_args):
        args.http_app = '../public-sample/'

    def get_http_app_path(self, httpio, root_path, request_path, translate_path):
        request_path = request_path.lstrip('/')

        if request_path == '':
            translate_path = root_path + '/routing-demo/index.html'
        elif request_path == 'hello':
            translate_path = root_path + '/static-sample/hello.html'
        elif request_path == 'basic':
            translate_path = root_path + '/basic.py'

        return translate_path


class MyObjectFactory(ObjectFactory):
    def create_pipeline(self):
        return MyPipeline()


if __name__ == '__main__':
    factory = MyObjectFactory()

    cmd = IpServerCmd(factory)

    cmd.run()
