import logging

from ipserver import __version__
from ipserver.configs import Constant
from ipserver.server.socket_server import SocketServer
from ipserver.util.data_io import DataOutput
from ipserver.util.sys_util import AppException
from ipserver.util.sys_util import Output, System
from logging import getLogger


class ViewHelper:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ViewHelper()

        return cls._instance

    def __init__(self):
        self.data_output = None
        self.quiet = False
        self.output_max = None

    def initialize(self, data_output, args):
        self.data_output = data_output
        self.output_target = args.fixed_output_target
        self.quiet = args.quiet
        self.output_max = args.output_max

    def show_help(self):
        width = 18

        self.line('[Command help]')
        self.line('send:'.ljust(width) + 'Begin input to send. Send by a Line-break. The shortcut is `s`.')
        self.line('bulk:'.ljust(width) + 'Begin bulk input to send. Send by Ctrl-key. The shortcut is `b`.')
        self.line('"1,2,3,..":'.ljust(width) + 'Switch the connection.')
        self.line('current:'.ljust(width) + 'Show current connection.')
        self.line('latest:'.ljust(width) + 'Switch latest connection.')
        self.line('list:'.ljust(width) + 'List the connections.')
        self.line('close:'.ljust(width) + 'Close current connection.')
        self.line('refresh:'.ljust(width) + 'Refresh connections.')
        self.line('exit:'.ljust(width) + 'Exit.')
        self.line('help:'.ljust(width) + 'Show help.')
        self.line('')

    def show_head(self, args):
        if not args.quiet:
            width = 18

            self.line('Mode: '.ljust(width) + args.mode)

            self.line('Bind:'.ljust(width) + str(args.bind))
            self.line('Port:'.ljust(width) + str(args.port))

            if args.mode in Constant.HTTP_MODES:
                self.line('HTTP opt:'.ljust(width) + args.http_opt)

            if args.forwarding:
                self.line('Forwarding:'.ljust(width) + args.forwarding)

            self.line('Input:'.ljust(width) + str(args.input))
            self.line('Output:'.ljust(width) + str(args.output))
            self.line('Output target:'.ljust(width) + str(args.output_target))

            self.line('Timeout:'.ljust(width) + str(args.timeout))
            self.line('Max connections:'.ljust(width) + str(args.max_connections))

            self.line('Dumpfile:'.ljust(width) + str(args.dumpfile))

            if args.mode == Constant.MODE_SSL:
                ssl_context = args.ssl_context if args.ssl_context is not None else 'auto'
                self.line('SSL context: '.ljust(width) + ssl_context)

            self.line('')

    def stopped(self):
        self.line('Stopped by user...\n')

    def show_bulk_mode(self):
        if not System.verify_os(True):
            msg = 'Press `Ctrl+D` to send.'
        else:
            msg = 'Press `Ctrl+Z` to send.'

        self.info('Please input send-data. ' + msg + '\n')

    def show_version(self):
        System.exit(Constant.APP_NAME + ' by ' + Constant.PYPI_NAME + ' ' + __version__)

    def show_conn_sock(self, conn_sock):
        self.line('ID: {}'.format(conn_sock.conn_id))
        self.line('Client IP: {}'.format(conn_sock.addr[0]))
        self.line('Client port: {}'.format(conn_sock.addr[1]))
        self.line('')

    def accepted(self, conn_sock):
        msg = self.create_message('Accepted from {host}', conn_sock)

        self.output_logging(msg)

    def receive(self, binary, conn_sock):
        msg = self.create_message('Receive {} bytes from {{host}}'.format(len(binary)), conn_sock)

        self.output_logging(msg)

        if self.data_output.mode != DataOutput.OUTPUT_NONE and self.output_target & Constant.DIRECTION_RECEIVE:
            self.output_data(binary)

    def send(self, binary, conn_sock):
        msg = self.create_message('Send {} bytes to {{host}}'.format(len(binary)), conn_sock)

        self.output_logging(msg)

        if self.data_output.mode != DataOutput.OUTPUT_NONE and self.output_target & Constant.DIRECTION_SEND:
            self.output_data(binary)

    def closed_socket(self, conn_sock):
        msg = self.create_message('Closed from {host}', conn_sock)

        self.output_logging(msg)

    def forwarding_send(self, binary, forwarding_socket, conn_sock):
        msg = self.create_message('Forwarding-send to' + forwarding_socket.hostname + ':' + str(forwarding_socket.port) + ' / ' + str(len(binary)) + ' bytes', conn_sock)

        getLogger(__name__).debug(msg)

    def forwarding_receive(self, binary, forwarding_socket, conn_sock):
        msg = self.create_message('Forwarding-receive from' + forwarding_socket.hostname + ':' + str(forwarding_socket.port) + ' / ' + str(len(binary)) + ' bytes', conn_sock)

        getLogger(__name__).debug(msg)

    def output_data(self, binary):
        attention = None

        if self.output_max > 0:
            if len(binary) > self.output_max:
                binary = binary[:self.output_max]
                binary += '\n...'.encode()
                attention = '\n\nData longer than {} bytes has been omitted. Refer to `--output_max` option.'.format(self.output_max) + '\n'

        self.line(self.data_output.get_data(binary))

        if attention:
            self.warn(attention)

    def output_error(self, e, prefix='', suffix=''):
        exc_info = Output.is_logging(logging.DEBUG)
        getLogger(__name__).error(str(e), exc_info=exc_info)

        msg = ''

        if not Output.is_logging(logging.DEBUG):
            msg = '\n\nSet `--debug` or `--verbose=3` option to output error detail.'

        error = SocketServer.get_error(e)

        prefix_msg = '\n' + prefix

        if error:
            self.warn(prefix_msg + error + suffix + '\n')
        elif isinstance(e, AppException):
            self.warn(prefix_msg + str(e) + suffix + '\n')
        else:
            self.warn(prefix_msg + 'An error has occurred.' + msg + suffix + '\n')

    def create_message(self, message, conn_sock):
        host = conn_sock.addr[0] + ':' + str(conn_sock.addr[1])
        message = message.format(host=host)

        return '[{}] {}'.format(conn_sock.conn_id, message)

    def output_message(self, message, conn_sock, warn=True):
        msg = self.create_message(message, conn_sock)

        if warn:
            self.warn('\n' + msg)
        else:
            self.info('\n' + msg)

    def line(self, v):
        if not self.quiet:
            Output.line(v)

    def info(self, v):
        if not self.quiet:
            Output.info(v)

    def warn(self, v):
        if not self.quiet:
            Output.warn(v)

    def print(self, v):
        if self.quiet != 2:
            Output.line(v)

    def output_line(self, msg, prefix_nl=True):
        if prefix_nl:
            msg = '\n' + msg

        self.line(msg)

    def output_info(self, msg, prefix_nl=True):
        if prefix_nl:
            msg = '\n' + msg

        self.info(msg)

    def output_warn(self, msg, prefix_nl=True):
        if prefix_nl:
            msg = '\n' + msg

        self.warn(msg)

    def output_logging(self, msg):
        self.output_warn(msg)

        getLogger(__name__).info(msg)
