class Constant:
    PYPI_NAME = 'ipserver'

    APP_NAME = 'ipserver'

    APP_DESCRIPTION = '`ipserver` is simple server on "TCP, UDP, SSL, HTTP, HTTPS" for debugging or network investigation. It supports interactive mode and forwarding, and can run Python program over HTTP or any other protocol.'
    APP_BOTTOM_DESC = '''command examples:
  ipserver --mode=TCP --port=8001
  ipserver --mode=SSL --port=8443

  ipserver --port=8002 --forwarding=google.com:80
  ipserver --port=8002 --forwarding=tcp://google.com:80
  ipserver --port=8002 --forwarding=ssl://google.com:443

  ipserver --port=8002 --restrict_allow="192.168.2.10;192.168.10.0/24"
  ipserver --port=8002 --restrict_deny="192.168.10.101;192.168.10.102"

  ipserver --port=8001 --mode=HTTP
  ipserver --port=8002 --mode=HTTP --http_opt=INTERACTIVE

  ipserver --port=8002 --mode=HTTP --http_opt=FILE
  ipserver --http_file=./ --port=8002
  ipserver --http_file=1 --port=8002
  ipserver --http_file_upload=1 --port=8002

  ipserver --mode=HTTP --http_opt=APP --port=8002
  ipserver --http_app=./examples/ipserver/ --port=8002
  ipserver --http_app=1 --port=8002

  ipserver --mode=HTTP --http_opt=INFO --port=8002

  ipserver --mode=HTTP --http_opt=FORWARDING --forwarding=https://www.amazon.com --port=8002
  ipserver --http_forwarding=https://www.amazon.com --port=8002

  ipserver --port=8002 --http_file=./ --http_digest_auth=.htdigest
  ipserver --port=8002 --http_file_upload=./ --http_digest_auth="admin:123456"
  ipserver --port=8002 --http_app=1 --http_digest_auth="admin:d71fa85bc0ded05215b28dfd8ca14112"

  ipserver --port=8001 --quiet

  ipserver --conf=ipserver.json
  ipserver --conf=ipserver.json --quiet

  ipserver --port=8001 --verbose=2
  ipserver --port=8001 --debug

documents:
  Documentation site: https://deer-hunt.github.io/ipserver/
  PyPI: https://pypi.org/project/ipserver/
  Github: https://github.com/deer-hunt/ipserver/
'''
    CONF_FILE = 'ipserver.json'
    LOG_FILE = 'ipserver.log'

    QUIET_INTERVAL = 60
    RECV_BUF_SIZE = 65565

    MODE_TCP = 'TCP'
    MODE_UDP = 'UDP'
    MODE_SSL = 'SSL'
    MODE_HTTP = 'HTTP'
    MODE_HTTPS = 'HTTPS'

    INPUT_NONE = 'NONE'
    INPUT_TEXT = 'TEXT'
    INPUT_BINARY = 'BINARY'
    INPUT_HEX = 'HEX'
    INPUT_BASE64 = 'BASE64'

    OUTPUT_NONE = 'NONE'
    OUTPUT_TEXT = 'TEXT'
    OUTPUT_BINARY = 'BINARY'
    OUTPUT_HEX = 'HEX'
    OUTPUT_BASE64 = 'BASE64'

    HTTP_INTERACTIVE = 'INTERACTIVE'
    HTTP_FILE = 'FILE'
    HTTP_PASS = 'PASS'
    HTTP_APP = 'APP'
    HTTP_INFO = 'INFO'
    HTTP_FORWARDING = 'FORWARDING'

    DIRECTION_SEND = 1
    DIRECTION_RECEIVE = 2

    SSL_CONTEXTS = {
        'sslv3': 'PROTOCOL_SSLv3',
        'tls1.0': 'PROTOCOL_TLSv1',
        'tls1.1': 'PROTOCOL_TLSv1_1',
        'tls1.2': 'PROTOCOL_TLSv1_2',
        'tls1.3': 'PROTOCOL_TLSv1_3'
    }

    SSL_OPTIONS = [
        'ssl_context', 'ssl_keypath', 'ssl_certfile', 'ssl_keyfile'
    ]

    HTTP_MODES = [
        MODE_HTTP, MODE_HTTPS
    ]

    HTTP_OPTIONS = [
        'http_path', 'http_digest_auth', 'enable_file_upload'
    ]

    HTTP_DIGEST_REALM = 'digest'

    HTTP_FILE_MIMES = {
        '': 'text/plain', '.sh': 'text/plain'
    }

    HTTP_STATIC_FILES = r'\.(html?|css|js|jpe?g|png|gif|svg|webp|woff2?|ttf|otf|ico|xml|json|txt|md|pdf|mp4|mp3|webm|avi|mov|docx?|xlsx?|pptx?)$'

    HTTP_FILE_CMD = 'ipcmd'
    HTTP_FILE_UPLOAD = 'file-upload'

    DUMPFILE_DIR = 'dumpfiles'

    HTTP_MD5_SALT = 'ipsalt'


class Config:
    PRE_ARGUMENTS = {
        'verbose': {'default': 0, 'type': int, 'help': 'Verbose mode. [Level - 1:TRACE_ERROR, 2:INFO, 3:DEBUG]', 'choices': [0, 1, 2, 3]},
        'debug': {'default': False, 'help': '`--debug` is equivalent to `--verbose=3`.', 'action': 'store_true'},
        'info': {'default': False, 'help': '`--info` is equivalent to `--verbose=2`.', 'action': 'store_true'},
        'log': {'default': None, 'type': str, 'help': 'Verbose log filename.', 'metavar': '{string}'},
        'quiet': {'default': False, 'help': 'Hide to output message.', 'action': 'store_true'},
        'conf': {'default': None, 'type': str, 'help': 'Load arguments from conf file by JSON. e.g.: ipserver.json '}
    }

    ARGUMENTS = {
        'mode': {'default': 'TCP', 'type': str.upper, 'help': 'Listening mode. Default: TCP', 'choices': ['TCP', 'UDP', 'SSL', 'HTTP', 'HTTPS']},
        'input': {'default': 'TEXT', 'type': str.upper, 'help': 'Input format in interactive input. Default: TEXT', 'choices': ['TEXT', 'BINARY', 'HEX', 'BASE64']},
        'output': {'default': 'TEXT', 'type': str.upper, 'help': 'Output format. Default: TEXT', 'choices': ['NONE', 'TEXT', 'BINARY', 'HEX', 'BASE64']},
        'output_target': {'default': 'RECEIVE', 'type': str.upper, 'help': 'Output target.', 'choices': ['ALL', 'SEND', 'RECEIVE']},
        'output_max': {'default': 2048, 'type': int, 'help': 'Max output bytes.'},
        'dumpfile': {'default': False, 'help': 'Dump response data to files. Dir: `./dumpfiles/`', 'action': 'store_true'},

        'bind': {'default': '0.0.0.0', 'type': str, 'help': 'Bind IP. e.g. 127.0.0.1, localhost, 0.0.0.0', 'metavar': '{string}'},
        'port': {'default': 8000, 'type': int, 'help': 'Listen port.', 'metavar': '{int}'},
        'timeout': {'default': 30.0, 'type': float, 'help': 'Timeout. Default: 30.0', 'metavar': '{float}'},

        'restrict_allow': {'default': None, 'type': str, 'help': 'Restrict except for allowed IP. e.g. 192.168.10.101;192.168.10.0/24', 'metavar': '{string}'},
        'restrict_deny': {'default': None, 'type': str, 'help': 'Restrict specified IP. e.g. 192.168.10.101;192.168.10.0/24', 'metavar': '{string}'},

        'ssl_context': {'default': None, 'type': str.upper, 'help': 'SSL context. [SSLv3, TLS1.0, TLS1.1, TLS1.2, TLS1.3]', 'choices': ['SSLV3', 'TLS1.0', 'TLS1.1', 'TLS1.2', 'TLS1.3']},
        'ssl_keypath': {'default': '', 'type': str, 'help': 'Directory path for SSL key.', 'metavar': '{string}'},
        'ssl_certfile': {'default': '', 'type': str, 'help': 'SSL certfile name.', 'metavar': '{string}'},
        'ssl_keyfile': {'default': '', 'type': str, 'help': 'SSL keyfile name.', 'metavar': '{string}'},

        'forwarding': {'default': None, 'type': str, 'help': 'Forward. e.g. Forward proxy.', 'metavar': '{string}'},

        'http_opt': {'default': 'FILE', 'type': str.upper, 'help': 'Behaviors in HTTP option.', 'choices': ['INTERACTIVE', 'FILE', 'PASS', 'APP', 'INFO', 'FORWARDING']},
        'http_path': {'default': './', 'type': str, 'help': 'HTTP public directory.', 'metavar': '{string}'},
        'http_forwarding_convert_host': {'default': False, 'help': 'Convert hostname of content to `/` in HTTP forwarding.', 'action': 'store_true'},
        'http_digest_auth': {'default': '', 'type': str, 'help': 'Enable digest authentication. Set authentication setting.\nFile: .htdigest\n"User/Raw: admin2:123456"\n"User/MD5: admin2:d71fab~~~~dfca14112"', 'metavar': '{string}'},
        'enable_file_upload': {'default': 0, 'type': int, 'help': 'Enable file-upload in FILE mode. 1: Overwrite 2: New create only', 'metavar': '{int}'},

        'http_app': {'default': None, 'type': str, 'help': '`--http_app` is equivalent to `--mode=HTTP and --http_opt=APP`.', 'metavar': '{string}', 'group': 'shortcut'},
        'http_file': {'default': None, 'type': str, 'help': '`--http_file` is equivalent to `--mode=HTTP and --http_opt=FILE`.', 'metavar': '{string}', 'group': 'shortcut'},
        'http_file_upload': {'default': None, 'type': str, 'help': '`--http_file_upload` is equivalent to `--mode=HTTP and --http_opt=FILE and --enable_file_upload=1`.', 'metavar': '{string}', 'group': 'shortcut'},
        'http_forwarding': {'default': None, 'type': str, 'help': '`--mode=HTTP and --http_opt=FORWARDING`.', 'metavar': '{string}', 'group': 'shortcut'},

        'version': {'default': False, 'help': 'Show version information.', 'action': 'store_true'}
    }

    ARGUMENTS_GROUP_NAMES = {
        'shortcut': 'Shortcut'
    }
