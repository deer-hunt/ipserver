import copy
import html
import importlib.util
import io
import logging
import os
import re
import ssl
import sys
import urllib.parse
from datetime import datetime
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from logging import getLogger
from pathlib import Path
from socket import SocketIO
from urllib.parse import parse_qs

from multipart import parse_form_data

from ipserver.configs import Constant
from ipserver.server.http_server_module import HTTPDigestAuth, HttpFileUploader, QueueLogger
from ipserver.server.socket_server import TCPSocketServer, SSLSocketServer, ConnSock, SendQueue, SocketCloseError
from ipserver.util.sys_util import AppException
from ipserver.util.urlparser import URLParser


class HTTPSocketServer(TCPSocketServer):
    def __init__(self, factory, pipeline, args):
        super().__init__()

        self.factory = factory
        self.pipeline = pipeline
        self.args = args
        self.shared_object = {}

        QueueLogger.get_instance().initialize()

    def accept(self, add_conn=True):
        conn, addr = self.sock.accept()

        if self.timeout > 0:
            conn.settimeout(self.timeout)

        conn_sock = HTTPConnSock(conn, addr)

        if add_conn:
            self.conn_bucket.add_conn(conn_sock)

        conn_sock.handler = self.factory.create_http_handler(conn_sock, self.port, self.pipeline, self.args, self.shared_object)

        return conn_sock


class HTTPSSocketServer(SSLSocketServer):
    def __init__(self, factory, pipeline, args):
        super().__init__(args)

        self.factory = factory
        self.pipeline = pipeline
        self.args = args
        self.shared_object = {}

        QueueLogger.get_instance().initialize()

    def accept(self, add_conn=True):
        conn_sock = None

        try:
            sock, addr = self.sock.accept()

            if self.timeout > 0:
                sock.settimeout(self.timeout)

            getLogger(__name__).info('SSL_VERSION: ' + sock.version())

            conn_sock = HTTPConnSock(sock, addr)

            if add_conn:
                self.conn_bucket.add_conn(conn_sock)

            conn_sock.handler = self.factory.create_http_handler(conn_sock, self.port, self.pipeline, self.args, self.shared_object)
        except ssl.SSLError:
            logger = getLogger(__name__)
            logger.info('SSL connection error.', exc_info=logger.isEnabledFor(logging.DEBUG))

        return conn_sock


class HTTPConnSock(ConnSock):
    def __init__(self, sock, addr):
        super().__init__(sock, addr)

        self.handler = None
        self.interactive_queue = None

    def send_queue(self, binary):
        self.interactive_queue.send(binary)

    def set_interactive_queue(self, interactive_queue):
        self.interactive_queue = interactive_queue

    def send(self, binary):
        self.sock.sendall(binary)

        super().send(binary)

    def post_send(self, binary):
        if self.handler.close_connection:
            raise SocketCloseError()

    def receive(self):
        self.handler.receive()

        binary = self.handler.rfile.pull_data()

        super().receive()

        return binary

    def complete_receive(self, binary):
        send_data = self.handler.wfile.getvalue()

        self.handler.wfile.truncate(0)
        self.handler.wfile.seek(0)

        QueueLogger.get_instance().flush()

        return send_data


class HttpIo:
    def __init__(self, method, request_path, environ, req_headers, gets, posts, post_data):
        # Request
        self.method = method
        self.request_path = request_path
        self.root_path = None
        self.is_directory = False
        self.directory_path = None
        self.environ = environ
        self.req_headers = req_headers

        self.gets = gets
        self.posts = posts
        self.post_data = post_data

        # Response
        self.status = 200
        self.content_type = 'text/html'
        self.keep_alive = 0
        self.auto_header = True
        self.res_headers = {}
        self.body = ''

    def set_dir(self, root_path, is_directory, directory_path):
        self.root_path = root_path
        self.is_directory = is_directory
        self.directory_path = directory_path

    def add_header(self, name, value):
        self.res_headers[name] = value

    def print(self, v, nl=True):
        v = str(v)

        if nl:
            v += '\n'

        self.body += v

    def print_byte(self, v, append=False):
        if not append:
            self.body = b''

        self.body += v


class BufferedReader(io.BufferedReader):
    def __init__(self, socket_io, buf_size):
        super().__init__(socket_io, buf_size)

        self.binary = b''

    def reset(self):
        self.binary = b''

    def read(self, *args, **kwargs):
        binary = super().read(*args, **kwargs)

        self.binary += binary

        return binary

    def readline(self, *args, **kwargs):
        binary = super().readline(*args, **kwargs)

        self.binary += binary

        return binary

    def pull_data(self):
        binary = self.binary

        self.reset()

        return binary


class HTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, conn_sock, port, pipeline, args, shared_object):
        """
        :param conn_sock:
        :type conn_sock: ConnSock
        :param port:
        :type port: int
        :param pipeline:
        :type pipeline: ipserver.core.pipeline.Pipeline
        :param args:
        :type args: Object
        :param shared_object:
        :type shared_object: dict
        """
        self.request = None
        self.pipeline = pipeline
        self.port = port
        self.client_address = conn_sock.addr[0]
        self.server = None
        self.http_path = args.http_path
        self.http_opt = args.http_opt
        self.http_digest_auth = args.http_digest_auth
        self.enable_file_upload = args.enable_file_upload if self.http_opt == Constant.HTTP_FILE else 0
        self.forwarding = args.forwarding
        self.forwarding_requester = None
        self.forwarding_convert_host = args.http_forwarding_convert_host
        self.url_parser = URLParser()
        self.interactive_queue = None
        self.command = None
        self.path = None
        self.directory = os.getcwd()
        self.conn_sock = conn_sock
        self.protocol_version = 'HTTP/1.1'
        self.close_connection = False
        self.default_charset = 'utf-8'
        self.headers = None
        self.translated_path = None
        self.logger = getLogger('queue')

        self.rfile = self._create_rfile(conn_sock.sock)
        self.wfile = io.BytesIO()

        self.shared_object = shared_object

        if self.http_opt == Constant.HTTP_INTERACTIVE:
            self.interactive_queue = SendQueue()
            conn_sock.set_interactive_queue(self.interactive_queue)

    def create_http_digest_auth(self, httpio):
        """
        :param httpio:
        :type httpio: HttpIo
        """
        return HTTPDigestAuth(httpio, self.command, self.path, self.pipeline)

    def create_http_file_uploader(self):
        return HttpFileUploader(self.pipeline)

    def _create_rfile(self, sock):
        return BufferedReader(SocketIO(sock, 'r'), Constant.RECV_BUF_SIZE)

    def set_forwarding_requester(self, forwarding_requester):
        self.forwarding_requester = forwarding_requester

    def receive(self):
        self.handle_one_request()

    def translate_path(self, path):
        if self.translated_path is not None:
            return self.translated_path

        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]

        try:
            path = urllib.parse.unquote(path, errors='surrogatepass')
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)

        path = os.path.normpath(path)

        root_path = os.path.abspath(self.http_path)

        return os.path.join(root_path, path.lstrip('/'))

    def parse_request(self):
        self.extensions_map.update(Constant.HTTP_FILE_MIMES)

        success = super().parse_request()

        if self.command is not None:
            self.logger.debug('REQUEST_PATH: ' + self.path)
        else:
            raise AppException('HTTP protocol error.(Illegal data or Other protocol)')

        return success

    def do_HEAD(self):
        self._respond_by_method(super().do_HEAD)

    def do_GET(self):
        self._respond_by_method(super().do_GET)

    def do_POST(self):
        self._respond_by_method(super().do_GET)

    def _parse_get_parameters(self, environ):
        gets = {key: value[0] if len(value) == 1 else value for key, value in parse_qs(environ['QUERY_STRING']).items()}

        return gets

    def _read_post_parameters(self, environ):
        """
        :param environ:
        :type environ: dict
        """
        post_data = None
        posts = None

        if self.command == 'POST':
            if not self._is_multipart(environ):
                post_data = self.rfile.read(int(self.headers.get('content-length')))
                post_data = post_data.decode('utf-8')
                posts = {key: value[0] if len(value) == 1 else value for key, value in parse_qs(post_data).items()}
            else:
                posts = self._parse_multipart(environ)

        return posts, post_data

    def _is_multipart(self, environ):
        """
        :param environ:
        :type environ: dict
        """
        content_type = environ.get('CONTENT_TYPE')

        return content_type.split(';', 1)[0].strip().lower() == 'multipart/form-data'

    def _parse_multipart(self, environ):
        """
        :param environ:
        :type environ: dict
        """
        environ = {**environ, **{'wsgi.input': self.rfile}}

        forms, files = parse_form_data(environ)

        posts = {}

        for name in forms:
            f = forms.get(name)
            posts[name] = f
            self.logger.debug('MULTIPART: ' + name)

        for name in files:
            f = files.get(name)
            posts[name] = f
            # f.name, f.filename, f.size, f.headerlist, f.value, f.file
            self.logger.debug('MULTIPART: ' + name + ', ' + f.filename)

        return posts

    def _get_directory_path(self, environ):
        """
        :param environ:
        :type environ: dict
        """
        translated_path = environ['PATH_TRANSLATED']

        is_directory = False

        if os.path.isdir(translated_path):
            is_directory = True
            directory_path = translated_path
        else:
            directory_path = os.path.dirname(translated_path)

        directory_path = directory_path.rstrip('/') + '/'

        return is_directory, directory_path

    def _respond_by_method(self, super_method):
        status = 0

        try:
            environ = self._build_environ()

            posts, post_data = self._read_post_parameters(environ)

            httpio = self._build_httpio(environ, posts, post_data)

            http_opt = self.pipeline.pre_http_process(self.http_opt, self.path, httpio)

            if self.enable_file_upload > 0:
                if not self.pipeline.is_enable_file_upload(httpio, self.path):
                    self.enable_file_upload = 0

            if self.http_digest_auth:
                if not self._process_digest_auth(httpio):
                    return

            if http_opt == Constant.HTTP_INTERACTIVE:
                self._respond_interactive(httpio)
            elif http_opt == Constant.HTTP_FILE:
                self._respond_file(httpio, super_method)
            elif http_opt == Constant.HTTP_APP:
                self._respond_app(httpio, super_method)
            elif http_opt == Constant.HTTP_INFO:
                self._respond_info(httpio)
            elif http_opt == Constant.HTTP_FORWARDING:
                self._request_forwarding(httpio)
            elif http_opt == Constant.HTTP_PASS:
                self._respond_content(httpio)

            status = httpio.status
        except Exception:
            status = 500

            msg = 'HTTP 500 Error'

            self.send_error(status, 'Error')

            self.logger.error(msg, exc_info=True)

        self._log_response(status)

    def _log_response(self, status):
        size = self.wfile.getbuffer().nbytes

        self.logger.info('[{}] {} "{}" {} {}'.format(self.conn_sock.conn_id, self.conn_sock.addr[0], self.requestline, status, size))
        self.logger.critical('[{}] "{}" {}'.format(self.conn_sock.conn_id, self.requestline, status))

    def _build_httpio(self, environ, posts, post_data):
        is_directory, directory_path = self._get_directory_path(environ)

        gets = self._parse_get_parameters(environ)

        httpio = self.create_httpio(environ, gets, posts, post_data)

        root_path = os.path.abspath(self.http_path)

        httpio.set_dir(root_path, is_directory, directory_path)

        return httpio

    def create_httpio(self, environ, gets, posts, post_data):
        return HttpIo(self.command, self.path, environ, self.headers, gets, posts, post_data)

    def _process_digest_auth(self, httpio):
        """
        :param httpio:
        :type httpio: HttpIo
        """
        digest_auth = self.create_http_digest_auth(httpio)

        digest_auth.load(self.http_digest_auth)

        auth_data = digest_auth.verify_authed(self.headers)

        if auth_data is not None:
            username = auth_data['username']

            httpio.environ['REMOTE_USER'] = username
            self.logger.info('DIGEST_AUTH_USER: {}'.format(username))
        else:
            digest_auth.authenticate()

            self._respond_content(httpio)

            return False

        return True

    def _respond_interactive(self, httpio):
        binary = self.interactive_queue.get()

        for i in range(self.interactive_queue.qsize()):
            binary += self.interactive_queue.get(False)

        httpio.body = binary

        self._respond_content(httpio)

    def _respond_file(self, httpio, super_method):
        if self._is_file_upload(httpio):
            http_file_uploader = self.create_http_file_uploader()

            http_file_uploader.dispatch(httpio, self.enable_file_upload)

            self._respond_content(httpio)
        else:
            super_method()

    def _is_file_upload(self, httpio):
        gets = httpio.gets

        if self.enable_file_upload > 0 and httpio.is_directory and gets.get(Constant.HTTP_FILE_CMD) == Constant.HTTP_FILE_UPLOAD:
            return True

        return False

    def _respond_app(self, httpio, super_method):
        translate_path = self.translate_path(self.path)

        translated_path = self.pipeline.get_http_app_path(httpio, httpio.root_path, self.path, translate_path)

        if translated_path is not None:
            translate_path = self.translated_path = translated_path

        path = Path(translate_path)

        if not re.search(r'\.py$', translate_path, flags=re.I):
            self._respond_static_file(httpio, path, super_method)
            return

        file_path = str(path.resolve())

        self.logger.debug('FILE_PATH: ' + file_path)

        try:
            if not path.exists():
                raise ModuleNotFoundError()

            sys.path.append(str(path.parent))

            spec = importlib.util.spec_from_file_location(path.name, file_path)

            module = importlib.util.module_from_spec(spec)

            module.httpio = httpio
            module.shared_object = self.shared_object
            module.conn_sock = self.conn_sock

            spec.loader.exec_module(module)

            self._respond_content(httpio)
        except ModuleNotFoundError:
            httpio.status = 404
            self.send_error(httpio.status, None)

    def _respond_static_file(self, httpio, path, super_method):
        load_static = False

        if not path.exists():
            load_static = True
        elif os.path.isdir(path):
            for filename in ['index.html', 'index.htm']:
                index = os.path.join(path, filename)
                if os.path.exists(index):
                    load_static = True
        elif re.search(Constant.HTTP_STATIC_FILES, str(path), flags=re.I):
            load_static = True

        if load_static:
            super_method()
        else:
            httpio.status = 403
            self.send_error(httpio.status, None)

    def _respond_info(self, httpio):
        values = {
            'Method': self.command,
            'Path': self.path,
            **self.headers
        }

        now = datetime.now()
        data = 'Time: {}\n'.format(now.strftime('%Y-%m-%d %H:%M:%S.%f'))

        for k, v in values.items():
            data += k + ': ' + v + '\n'

        if self.command == 'POST':
            data += '\n' + httpio.post_data + '\n'

        httpio.body = '<html><body><pre>\n' + data + '\n</pre></body></html>'

        self._respond_content(httpio)

    def _request_forwarding(self, httpio):
        url = self.forwarding.rstrip('/ ') + self.path

        forwarding_url = self.url_parser.parse_url(url)

        req_headers = copy.deepcopy(self.headers)

        del req_headers['Host']
        del req_headers['Accept-Encoding']

        forwarding_url = self.pipeline.pre_http_forwarding_request(httpio, forwarding_url, req_headers)

        self.logger.debug('Forwarding request to ' + url)

        response, binary = self.forwarding_requester.request(self.command, forwarding_url, req_headers, httpio.post_data)

        self.logger.debug('Forwarding response is ' + str(len(binary)) + ' bytes')

        res_headers = response.msg

        if self.forwarding_convert_host and self._is_convert_forwarding(res_headers):
            binary = self._convert_forwarding_host(binary, res_headers, forwarding_url)

            self.logger.debug('Forwarding converted response is ' + str(len(binary)) + ' bytes')

        binary = self.pipeline.post_http_forwarding_request(httpio, forwarding_url, req_headers, res_headers, response, binary)

        httpio.status = response.status

        httpio.content_type = res_headers['Content-Type']

        del res_headers['Content-Type']
        del res_headers['Content-Length']
        del res_headers['Transfer-Encoding']

        httpio.res_headers = res_headers
        httpio.body = binary

        self._respond_content(httpio)

    def _is_convert_forwarding(self, res_headers):
        content_type = res_headers['Content-Type']

        if content_type is not None and re.search(r'(text|javascript)', content_type):
            return True

        return False

    def _convert_forwarding_host(self, binary, res_headers, forwarding_url):
        request_host = self._get_forwarding_replace_host(forwarding_url.hostname)

        hostname = r'\1/'

        binary = re.sub(request_host.encode(), hostname.encode(), binary)

        return binary

    def _get_forwarding_replace_host(self, v):
        v = re.sub(r'^www\.', '', v, flags=re.I)

        if not re.search(r'\.[0-9a-z-]{1,63}\.[a-z]{2,}$', v, flags=re.I):
            v = r'(www\.)?' + re.escape(v)
        else:
            v = re.escape(v)

        v = r'(=\s*["\']*\s*)(https?://|//)?' + v + r'(:\d+)?/?'

        return v

    def _respond_content(self, httpio):
        self.pipeline.pre_http_respond(httpio)

        content = httpio.body

        if isinstance(content, str):
            binary = content.encode()
        else:
            binary = content

        if not httpio.res_headers.get('Date'):
            self.send_response(httpio.status)
        else:
            self.send_response_only(httpio.status)

        if httpio.auto_header:
            self.send_header('Content-Type', httpio.content_type)
            self.send_header('Content-Length', len(binary))

            if httpio.keep_alive > 0:
                self.send_header('Connection', 'Keep-Alive')
                self.send_header('Keep-Alive', 'timeout={}, max=100'.format(httpio.keep_alive))

        if len(httpio.res_headers) > 0:
            for k, v in httpio.res_headers.items():
                self.send_header(k, str(v))

        self.end_headers()

        self.wfile.write(binary)

    def guess_type(self, path):
        ctype = super().guess_type(path)

        if ctype == 'text/plain':
            ctype += '; charset=' + self.default_charset

        return ctype

    def send_head(self):
        path = self.translate_path(self.path)

        if self.http_opt == Constant.HTTP_FILE:
            if os.path.isdir(path):
                return self.list_directory(path)

        return super().send_head()

    '''
    Extend SimpleHTTPRequestHandler::list_directory
    '''

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(
                HTTPStatus.NOT_FOUND,
                'No permission to list directory')
            return None

        list.sort(key=lambda a: a.lower())

        if not re.search(r'^/[^/]*$', self.path):
            list.insert(0, '..')

        r = []
        try:
            displaypath = urllib.parse.unquote(self.path,
                                               errors='surrogatepass')
        except UnicodeDecodeError:
            displaypath = urllib.parse.unquote(path)
        displaypath = html.escape(displaypath, quote=False)
        enc = sys.getfilesystemencoding()
        title = 'Directory listing for %s' % displaypath
        r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                 '"http://www.w3.org/TR/html4/strict.dtd">')
        r.append('<html>\n<head>')
        r.append('<meta http-equiv="Content-Type" content="text/html; charset=%s">' % enc)
        r.append('<style>.overview{display: flex;justify-content: space-between;}.right-link{margin:10px;}</style>')
        r.append('<title>%s</title>\n</head>' % title)
        r.append('<body><div class="overview">')
        r.append('<h1>%s</h1>' % title)

        if self.enable_file_upload > 0:
            right_link = '<div><a href="?{}">Upload file</a></div>'.format(
                Constant.HTTP_FILE_CMD + '=' + Constant.HTTP_FILE_UPLOAD)
        else:
            right_link = ''

        r.append('<div class="right-link">%s</div>' % right_link)
        r.append('</div>')

        r.append('<hr>\n')

        r.append('<ul>')
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            r.append('<li><a href="%s">%s</a></li>'
                     % (urllib.parse.quote(linkname, errors='surrogatepass'),
                        html.escape(displayname, quote=False)))
        r.append('</ul>\n<hr>\n</body>\n</html>\n')
        encoded = '\n'.join(r).encode(enc, 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f

    '''
    Refer: CGIHTTPRequestHandler::run_cgi
    '''

    def _build_environ(self):
        # find an explicit query string, if present.
        rest, _, query = self.path.partition('?')

        # dissect the part after the directory name into a script name &
        # a possible additional path, to be stored in PATH_INFO.
        i = rest.find('/')
        if i >= 0:
            _, rest = rest[:i], rest[i:]
        else:
            _, rest = rest, ''

        # Reference: http://hoohoo.ncsa.uiuc.edu/cgi/env.html
        # XXX Much of the following could be prepared ahead of time!
        env = {}
        env['SERVER_SOFTWARE'] = self.version_string()

        env['SERVER_PROTOCOL'] = self.protocol_version
        env['SERVER_PORT'] = str(self.port)
        env['REQUEST_METHOD'] = self.command
        uqrest = urllib.parse.unquote(rest)
        env['PATH_INFO'] = uqrest

        translated_path = self.translate_path(uqrest)
        env['PATH_TRANSLATED'] = translated_path
        env['PATH_RELATIVE'] = os.path.relpath(translated_path)

        if query:
            env['QUERY_STRING'] = query

        env['REMOTE_ADDR'] = self.client_address

        # XXX REMOTE_IDENT
        if self.headers.get('content-type') is None:
            env['CONTENT_TYPE'] = self.headers.get_content_type()
        else:
            env['CONTENT_TYPE'] = self.headers['content-type']
        length = self.headers.get('content-length')
        if length:
            env['CONTENT_LENGTH'] = length
        referer = self.headers.get('referer')
        if referer:
            env['HTTP_REFERER'] = referer
        accept = []
        for line in self.headers.getallmatchingheaders('accept'):
            if line[:1] in "\t\n\r ":
                accept.append(line.strip())
            else:
                accept = accept + line[7:].split(',')
        env['HTTP_ACCEPT'] = ','.join(accept)
        ua = self.headers.get('user-agent')
        if ua:
            env['HTTP_USER_AGENT'] = ua
        co = filter(None, self.headers.get_all('cookie', []))
        cookie_str = ', '.join(co)
        if cookie_str:
            env['HTTP_COOKIE'] = cookie_str
        # XXX Other HTTP_* headers
        # Since we're setting the env in the parent, provide empty
        # values to override previously set values
        for k in ('QUERY_STRING', 'REMOTE_HOST', 'CONTENT_LENGTH',
                  'HTTP_USER_AGENT', 'HTTP_COOKIE', 'HTTP_REFERER'):
            env.setdefault(k, "")

        return env

    def log_message(self, format, *args):
        pass

    def version_string(self):
        return Constant.APP_NAME

    def send_error(self, code, message=None, explain=None):
        if code == 404:
            self.error_message_format = '<!DOCTYPE html><html><head><title>404 Not Found</title></head><body><h1>404 Not Found</h1><p>The requested URL was not found on this server.</p></body></html>'
        elif code == 403:
            self.error_message_format = '<!DOCTYPE html><html><head><title>403 Forbidden</title></head><body><h1>403 Forbidden</h1><p>You do not have permission to access this resource on the server.</p></body></html>'

        super().send_error(code, message, explain)
