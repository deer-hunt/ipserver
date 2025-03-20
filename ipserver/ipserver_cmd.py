import re
import signal
import sys
import time

from ipserver.configs import Config, Constant
from ipserver.core.object_factory import ObjectFactory
from ipserver.core.pipeline import Pipeline
from ipserver.service.view_helper import ViewHelper
from ipserver.util.data_io import InteractiveInput


class IpServerCmd:
    def __init__(self, factory):
        self.factory = factory  # type: ObjectFactory
        self.pipeline = self.factory.create_pipeline()  # type: Pipeline
        self.config = self.factory.get_config()  # type: Config

        self.socket_server = None
        self.conn_bucket = None
        self.data_input = None
        self.data_output = None
        self.interactive_input = None

        self.view = None  # type: ViewHelper

    def run(self):
        try:
            self._pre_initialize()

            args, parser = self._parse_args()

            self._initialize(args)

            self._verify_args(args, parser)

            self.dispatch(args)
        except Exception as e:
            self.view.output_error(e)

    def _verify_args(self, args, parser):
        if args.version:
            self.view.show_version()
        elif len(sys.argv) == 1:
            parser.print_help()
            sys.exit()

    def _pre_initialize(self):
        self.view = self.factory.create_view_helper()

    def _initialize(self, args):
        self.conn_bucket = self.factory.create_conn_bucket()

        self.socket_server = self._create_socket_server(args)
        self.socket_server.initialize(self.conn_bucket, args.timeout)

        self.data_input = self.factory.create_data_input()
        self.data_input.initialize(args.input)

        data_output = self.factory.create_data_output()
        data_output.initialize(args.output)

        self.view.initialize(data_output, args)

        self.interactive_input = self.factory.create_interactive_input()

        self.pipeline.initialize(self.config, self.socket_server)

        signal.signal(signal.SIGINT, self.signal_stop)

    def _create_socket_server(self, args):
        socket_server = None

        mode = args.mode
        ssl_context = args.fixed_ssl_context

        if mode == Constant.MODE_TCP:
            socket_server = self.factory.create_tcp_socket_server()
        elif mode == Constant.MODE_UDP:
            socket_server = self.factory.create_udp_socket_server()
        elif mode == Constant.MODE_SSL:
            socket_server = self.factory.create_ssl_socket_server(args)
            socket_server.set_ssl_context(ssl_context)
        elif mode == Constant.MODE_HTTP:
            socket_server = self.factory.create_http_socket_server(self.factory, self.pipeline, args)
        elif mode == Constant.MODE_HTTPS:
            socket_server = self.factory.create_https_socket_server(self.factory, self.pipeline, args)

        return socket_server

    def _parse_args(self):
        args_builder = self.factory.create_args_builder(self.config, self.pipeline)

        return args_builder.parse()

    def dispatch(self, args):
        self.view.show_head(args)

        self._listen_server(args)

        self._complete()

    def signal_stop(self, sig, frame):
        self.view.stopped()

        self._complete()

        sys.exit()

    def _listen_server(self, args):
        self.socket_server.create(args.port, args.bind)

        self.pipeline.create_socket(self.socket_server)

        self.socket_server.listen()

        conn_sock_listener = self.factory.create_conn_sock_listener(self.socket_server, self.conn_bucket, args, self.factory, self.pipeline, self.view)

        conn_sock_listener.start()

        if not args.quiet:
            self._listen_input(args)
        else:
            self._listen_quiet()

    def _listen_input(self, args):
        self.view.show_help()

        conn_sock = None

        while True:
            action, line = self.interactive_input.get_input()

            self.conn_bucket.refresh()

            self.pipeline.interactive_input(action, line, conn_sock, self.conn_bucket)

            conn_sock = self._interactive_action(conn_sock, action, line, args)

    def _interactive_action(self, conn_sock, action, line, args):
        if action == InteractiveInput.ACTION_COMMAND:
            if re.search(r'^\d+$', line):
                id = int(line)

                t_conn_sock = self.conn_bucket.get_conn(id)

                if t_conn_sock:
                    conn_sock = self._select_conn_sock(t_conn_sock)
                    self.view.output_message('Switched.', conn_sock)
                else:
                    self.view.output_warn('Not available connection.[{}]'.format(id))
            elif line == 'send' or line == 's':
                conn_sock = self._select_conn_sock(conn_sock)

                if conn_sock is not None:
                    self.interactive_input.switch_input()
                    self.view.output_info('Please input data to send...\n')
            elif line == 'bulk' or line == 'b':
                conn_sock = self._select_conn_sock(conn_sock)

                if conn_sock is not None:
                    self.interactive_input.switch_text_mode()
                    self.view.show_bulk_mode()
            elif line == 'current':
                conn_sock = self._select_conn_sock(conn_sock)

                if conn_sock is not None:
                    self.view.show_conn_sock(conn_sock)
            elif line == 'latest':
                conn_sock = self._select_conn_sock(None)

                if conn_sock is not None:
                    self.view.output_message('Switched.', conn_sock)
            elif line == 'list':
                conn_socks = self.conn_bucket.get_conns()

                if len(conn_socks) > 0:
                    for conn_sock in conn_socks:
                        self.view.output_line(self.view.create_message('{host}', conn_sock), prefix_nl=False)
                else:
                    self.view.output_warn('There is no connection.')
            elif line == 'close':
                conn_sock = self._select_conn_sock(conn_sock)

                if conn_sock is not None:
                    conn_sock.close()
                    self.view.output_message('The connection is closed.', conn_sock)
            elif line == 'refresh':
                self.conn_bucket.refresh_connections()
                self.view.output_info('The connections were refreshed.')
            elif line == 'exit':
                self.socket_server.close()
                self.view.output_warn('Exit by user.')
                return
            elif line == 'help':
                self.view.show_help()
            else:
                self.view.output_warn('Unknown command')
        elif action == InteractiveInput.ACTION_INPUT and line:
            conn_sock = self._select_conn_sock(conn_sock)

            if conn_sock is not None:
                if args.mode in Constant.HTTP_MODES and args.http_opt != Constant.HTTP_INTERACTIVE:
                    self.view.output_warn('Not support interactive sending in current option.')
                    return

                conn_sock.send_queue(self.data_input.get_data(line))

                self.interactive_input.switch_command()

                self.view.output_message('Sent to {host}', conn_sock)

        return conn_sock

    def _listen_quiet(self):
        self.view.print('Starting ipserver in quiet mode...')

        while True:
            self.pipeline.kick_quiet()
            self.conn_bucket.refresh_connections()

            time.sleep(Constant.QUIET_INTERVAL)

    def _select_conn_sock(self, conn_sock):
        if conn_sock is not None:
            if not self.conn_bucket.get_conn(conn_sock.conn_id):
                self.view.output_warn('The connection is not available connection.', conn_sock)
                conn_sock = None

        if conn_sock is None:
            conn_sock = self.conn_bucket.get_max_conn_sock()

            if conn_sock is not None:
                self.view.output_message('Switched automatically.', conn_sock, warn=False)
            else:
                self.view.output_warn('The connection doesn\'t exist. Command is canceled.')

                self.interactive_input.switch_command()

        return conn_sock

    def _complete(self):
        self.pipeline.complete()
