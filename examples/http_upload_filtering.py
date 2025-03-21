from ipserver.core.object_factory import ObjectFactory
from ipserver.core.pipeline import Pipeline
from ipserver.ipserver_cmd import IpServerCmd
from datetime import datetime

import re

'''
Upload filtering.

Command:
# python3 upload_filtering.py --info --http_path='../../'
# curl http://develop-server:8000/
'''


class MyPipeline(Pipeline):
    def pre_configure(self, args):
        args.http_file_upload = 1

    def is_enable_file_upload(self, httpio, request_path):
        print(httpio.environ, request_path)  # Output STDOUT

        remote_addr = httpio.environ['REMOTE_ADDR']
        path_info = httpio.environ['PATH_INFO']

        if re.search(r'public-sample\/?$', path_info) and not re.search(r'127\.0\.0\.1', remote_addr):
            return True

        return False

    def pre_http_file_upload(self, httpio, mpart):
        date = datetime.now().strftime('%Y-%m-%d-%H%M')

        mpart.filename = re.sub(r'^.+\.([^.]+)$', '{}.\\1'.format(date), mpart.filename)

        return True

    def post_http_file_upload(self, httpio, mpart):
        pass


class MyObjectFactory(ObjectFactory):
    def create_pipeline(self):
        return MyPipeline()


if __name__ == '__main__':
    factory = MyObjectFactory()

    cmd = IpServerCmd(factory)

    cmd.run()
