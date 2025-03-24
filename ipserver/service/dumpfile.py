import os

from logging import getLogger
from ipserver.configs import Constant


class DumpFile:
    def __init__(self, pipeline):
        self.dirname = None
        self.pipeline = pipeline
        self.cur_direction = None

    def initialize(self, dirname):
        self.dirname = dirname.rstrip('/') + '/'

        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)

    def write(self, conn_sock, direction, binary):
        filename = self.get_filename(conn_sock, direction)
        path = self.dirname + filename

        getLogger(__name__).info('DUMPFILE_PATH: ' + path)

        with open(path, 'ab') as file:
            self.pipeline.pre_dump_write(file, binary, filename, conn_sock, direction)

            file.write(binary)

        return path

    def get_filename(self, conn_sock, direction, ext='.dat'):
        filename = Constant.DUMPFILE_PREFIX + str(conn_sock.conn_id) + '_' + str(conn_sock.sequence) + '_' + direction + '_' + conn_sock.addr[0] + '_' + str(conn_sock.addr[1]) + ext

        filename = self.pipeline.get_filename(conn_sock, direction, filename)

        return filename

    def get_path(self):
        full_path = os.path.abspath(self.dirname)

        return full_path.rstrip('/') + '/'

    def get_file_num(self):
        full_path = self.get_path()

        files = next(os.walk(full_path))[2]

        return len(files)
