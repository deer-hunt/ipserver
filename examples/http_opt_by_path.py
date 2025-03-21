from ipserver.core.object_factory import ObjectFactory
from ipserver.core.pipeline import Pipeline
from ipserver.ipserver_cmd import IpServerCmd
from datetime import datetime
from ipserver.configs import Constant

'''
Setting `http_opt` by path. Changing the behavior.

Command:
# python3 http_opt_by_path.py --port=8002

http://develop-server:8002/
http://develop-server:8002/info/
http://develop-server:8002/pass/
http://develop-server:8002/public-sample/hello.py
'''


class MyPipeline(Pipeline):
    def pre_configure(self, args):
        args.mode = 'HTTP'
        args.http_path = '../'

    def pre_http_process(self, http_opt, path, httpio):
        path = path.strip('/')

        if path == 'info':
            http_opt = Constant.HTTP_INFO
        elif path == 'pass':
            http_opt = Constant.HTTP_PASS
        elif path == 'public-sample/hello.py':
            http_opt = Constant.HTTP_APP

        return http_opt


class MyObjectFactory(ObjectFactory):
    def create_pipeline(self):
        return MyPipeline()


if __name__ == '__main__':
    factory = MyObjectFactory()

    cmd = IpServerCmd(factory)

    cmd.run()
