import hashlib
import importlib
import logging
import logging.handlers
import os
import queue
import random
import re
import shlex
import time
from logging import getLogger
from pathlib import Path

from ipserver.configs import Constant
from ipserver.service.view_helper import ViewHelper
from ipserver.util.sys_util import AppException


class QueueLogger:
    _instance = None

    @classmethod
    def get_instance(cls, name='queue'):
        if cls._instance is None:
            cls._instance = QueueLogger(name)

        return cls._instance

    def __init__(self, name='queue'):
        self.queue = queue.Queue()

        self.logger = getLogger(name)

    def initialize(self):
        level = getLogger().getEffectiveLevel()

        self.logger.setLevel(level)

        queue_handler = logging.handlers.QueueHandler(self.queue)
        self.logger.addHandler(queue_handler)

        self.logger.propagate = False

    def flush(self):
        while not self.queue.empty():
            log = self.queue.get()

            if log is not None:
                if log.levelno != logging.CRITICAL:
                    getLogger(__name__).handle(log)
                else:
                    ViewHelper.get_instance().warn(log.msg)
            else:
                break


class HTTPDigestAuth:
    def __init__(self, httpio, command, path, pipeline):
        self.httpio = httpio
        self.command = command
        self.path = path
        self.realm = Constant.HTTP_DIGEST_REALM
        self.users = {}
        self.pipeline = pipeline
        self.logger = getLogger('queue')

    def load(self, http_digest_auth):
        matches = re.search(r'^(.+):(.+)$', http_digest_auth)

        if matches:
            username = matches.group(1).strip()
            password = matches.group(2).strip()
            self.users[username] = password
        elif http_digest_auth != '1':
            file_path = http_digest_auth
            realm, self.users = self.load_from_file(file_path)

            if len(self.users) > 0:
                self.realm = realm

        self.pipeline.digest_auth_load(self.users)

        self.logger.debug('DIGEST_AUTH_USERS: ' + str(len(self.users)))

    def load_from_file(self, file_path):
        realm = None
        users = {}

        self.logger.debug('DIGEST_AUTH_FILE: ' + file_path)

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    row = list(map(str.strip, line.split(':')))

                    if len(row) == 3:
                        [username, trealm, password] = row

                        if realm is None:
                            realm = trealm

                        if username and realm and password:
                            users[username] = password

                if len(users) == 0:
                    raise AppException('Empty')
        except Exception as e:
            if isinstance(e, AppException):
                msg = 'HTTP Digest-auth file empty.({})'
            else:
                msg = 'HTTP Digest-auth file error.({})'

            msg = msg.format(file_path)

            self.logger.error(msg, exc_info=self.logger.isEnabledFor(logging.DEBUG))
            self.logger.critical(msg)

        return realm, users

    def verify_authed(self, headers):
        auth_data = self.parse_auth_header(headers)

        if auth_data is not None:
            username = auth_data.get('username')

            if self.pipeline.digest_auth_veirfy(self.httpio, username, auth_data, self.users):
                return auth_data

            password = self.users.get(username)

            if password and self.verify_user(auth_data, username, password):
                return auth_data

        return None

    def parse_auth_header(self, headers):
        auth_header = headers.get('Authorization')

        if auth_header is None:
            return None

        lexer = shlex.shlex(auth_header[7:], posix=True)
        lexer.quotes = '"'
        lexer.whitespace_split = True
        lexer.whitespace = ', '

        tokens = dict(token.split('=', 1) for token in lexer)

        return {k.strip(): v.strip() for k, v in tokens.items()}

    def verify_user(self, auth_data, username, password):
        if not self.is_md5(password):
            ha1 = self.create_md5_hash("{}:{}:{}".format(username, self.realm, password))
        else:
            ha1 = password

        ha2 = self.create_md5_hash("{}:{}".format(self.command, self.path))

        nonce = auth_data['nonce']
        nc = auth_data['nc']
        cnonce = auth_data['cnonce']

        valid_response = self.create_md5_hash("{ha1}:{nonce}:{nc}:{cnonce}:auth:{ha2}".format(ha1=ha1, nonce=nonce, nc=nc, cnonce=cnonce, ha2=ha2))

        if auth_data['response'] == valid_response:
            return True

        return False

    def is_md5(self, v):
        return True if re.match(r'^[a-f0-9]{32}$', v, flags=re.I) else False

    def authenticate(self):
        ha1 = self.create_md5_hash("{}:{}".format(time.time(), random.random()))

        self.httpio.status = 401
        self.httpio.res_headers['WWW-Authenticate'] = 'Digest realm="{}", qop="auth", nonce="{}"'.format(self.realm, ha1)
        self.httpio.body = '<!DOCTYPE html><html><head><title>401 Authentication Error</title></head><body><h1>Authentication Error(401)</h1><p>You need to provide valid credentials to access this resource.</p></body></html>'

    def create_md5_hash(self, data):
        return hashlib.md5(data.encode()).hexdigest()


class HttpFileUploader:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.logger = getLogger('queue')

    @staticmethod
    def load_multipart():
        module = None

        try:
            module = importlib.import_module('multipart')
        except Exception:
            raise AppException('`multipart` module is not found. `pip install multipart`.')

        return module

    def dispatch(self, httpio, mode):
        self.show_head(httpio)

        if httpio.posts:
            httpio.print('<h2>Result</h2>')

            if self.verify_token(httpio):
                self.save_file(httpio, 'upload_file', mode)
            else:
                httpio.print('<div class="red">Illegal error.</div>')
        else:
            self.show_form(httpio)

        self.show_foot(httpio)

    def show_head(self, httpio):
        html = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"><html><head>
        <title>Upload file({upload_path})</title>
        <style>
        body{{padding: 0px;margin-bottom: 80px;line-height: 20pt;}}
        .label{{width: 150px;}}
        .red{{color: red;}}
        .upload-pane{{padding-top: 40px;}}
        .btn-upload {{font-size: 13pt;padding: 8px 25px;}}
        </style>
        </head><body>
        <h1>Upload file</h1>
        <hr>
        <table>
        <tr><td class="label">Path: </td><td><a href="{upload_path}">{upload_path}</a></td></tr>
        <tr><td class="label">Files: </td><td>{files}</td></tr>
        </table>
        <hr>
        '''

        upload_path = self.get_upload_path(httpio)

        html = html.format(upload_path=upload_path, files=self.get_directory_files(httpio))

        httpio.print(html)

    def get_directory_files(self, httpio):
        translated_path = httpio.environ['PATH_TRANSLATED']

        return len(list(Path(translated_path).glob('*')))

    def show_form(self, httpio):
        token = self.create_token(httpio)

        html = '''
        <h2>Specify the file</h2>
        <form action="?{cmd}={action}" method="post" enctype="multipart/form-data">
        <table width="100%">
        <tr><td><input type="file" name="upload_file"></td></tr>
        <tr>
            <td colspan="2" class="upload-pane">
                <input type="hidden" name="token" value="{token}">
                <button type="submit" class="btn-upload">Upload</button>
            </td>
        </tr>
        </table>
        </form>
        '''

        html = html.format(token=token, cmd=Constant.HTTP_FILE_CMD, action=Constant.HTTP_FILE_UPLOAD)

        httpio.print(html)

    def verify_token(self, httpio):
        token = httpio.posts.get('token')

        ctoken = self.create_token(httpio)

        return True if token == ctoken else False

    def save_file(self, httpio, name, mode):
        done = False

        filename = ''

        if name in httpio.posts:
            mpart = httpio.posts[name]

            if mpart and mpart.file:
                filename = mpart.filename

                if not self.pipeline.pre_http_file_upload(httpio, mpart):
                    httpio.print('<div class="red">Validation error. ({})</div>'.format(mpart.filename))
                    return

                dir = httpio.directory_path
                filepath = dir + mpart.filename

                if not self.is_valid_filename(mpart.filename):
                    httpio.print('<div class="red">Filename error. ({})</div>'.format(mpart.filename))
                    return

                if mode == 2 and os.path.exists(filepath):
                    httpio.print('<div class="red">File already exists. ({})</div>'.format(mpart.filename))
                    return

                try:
                    with open(dir + mpart.filename, 'wb') as file:
                        file.write(mpart.file.read())
                        done = True

                    self.pipeline.post_http_file_upload(httpio, mpart)
                except Exception:
                    msg = 'HTTP File upload error.({})'.format(filename)

                    self.logger.error(msg, exc_info=self.logger.isEnabledFor(logging.DEBUG))
                    self.logger.critical(msg)

        if done:
            upload_path = self.get_upload_path(httpio)

            httpio.print('<div>Upload has completed. Uploaded path is <a href="{}">here</a>.</div>'.format(upload_path))
        else:
            httpio.print('<div class="red">Upload has failed.</div>')

    def is_valid_filename(self, filename):
        return False if re.search(r'(\.\.\|[/|*:\0])', filename) is not None else True

    def show_foot(self, httpio):
        httpio.print('</html>')

    def get_upload_path(self, httpio):
        return str(Path(httpio.request_path).parent).rstrip('/') + '/'

    def create_token(self, httpio):
        upload_path = self.get_upload_path(httpio)

        return self.create_md5(upload_path + ':' + Constant.HTTP_MD5_SALT)

    def create_md5(self, data):
        return hashlib.md5(data.encode()).hexdigest()
