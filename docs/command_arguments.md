# Command arguments

This document is a description of ipserver's command arguments.

## General and Debugging

### `--verbose`

Verbose mode. `Level - 1:TRACE_ERROR, 2:INFO, 3:DEBUG.`

- **Type:** `int`
- **Default:** `0`
- **Choices:**

| Value | Description                                         |
|-------|-----------------------------------------------------|
| 1     | TRACE_ERROR. Output error with trace.               |
| 2     | INFO. Output setting values and internal values.    |
| 3     | DEBUG. Output maximum debug information.            |

- **Example:**

```
--verbose=1
--verbose=2
--verbose=3
```

### `--debug`

`--debug` is equivalent to `--verbose=3`.

- **Type:** `bool`
- **Default:** `False`

- **Example:**

```
--debug
```

### `--info`

`--info` is equivalent to `--verbose=2`.

- **Type:** `bool`
- **Default:** `False`

- **Example:**

```
--info
```

### `--log`

Verbose log filename.

- **Type:** `str`
- **Default:** `None`

- **Example:**

```
--log=logfile.txt
```

### `--quiet`

Stop to output message. And Enable logging.

- **Type:** `bool`
- **Default:** `False`

- **Example:**

```
--quiet
```

### `--conf`

Load arguments from conf file by JSON. e.g. ipserver.json

- **Type:** `str`
- **Default:** `None`

- **Example:**

```
--conf=ipserver.json
```

## Main Arguments

### `--mode`

Listening mode. Default: TCP

- **Type:** `str`
- **Default:** `TCP`
- **Choices:**

| Value | Description |
|-------|-------------|
| TCP   | TCP protocol.     |
| UDP   | UDP protocol.    |
| SSL   | SSL protocol.    |
| HTTP  |  HTTP protocol.   |
| HTTPS | HTTP protocol via HTTPS.  |

- **Example:**

```
--mode=TCP
--mode=HTTP
--mode=SSL
```

### `--input`

Input format. Default: TEXT

- **Type:** `str`
- **Default:** `TEXT`
- **Choices:**

| Value  | Description |
|--------|-------------|
| TEXT   | Text format |
| BINARY | Binary format |
| HEX    | Hexadecimal format |
| BASE64 | Base64 encoded format |

- **Example:**

```
--input=TEXT
--input=HEX
```

### `--output`

Output format. Default: TEXT

- **Type:** `str`
- **Default:** `TEXT`
- **Choices:**

| Value  | Description |
|--------|-------------|
| NONE   | None            |
| TEXT   | Text format |
| BINARY | Binary format |
| HEX    | Hexadecimal format |
| BASE64 | Base64 encoded format |

- **Example:**

```
--output=TEXT
--output=NONE
--output=BASE64
```

### `--output_target`

Output target. Default: RECEIVE

- **Type:** `str`
- **Default:** `RECEIVE`
- **Choices:**

| Value  | Description |
|--------|-------------|
| ALL   | Both directions.            |
| SEND   | Only send. |
| RECEIVE | Only receive. |

- **Example:**

```
--output=ALL
--output=SEND
--output=RECEIVE
```

### `--output_max`

Max output bytes.

- **Type:** `int`
- **Default:** 10240
- **Choices:**

- **Example:**

```
--output_max=100000
```

### `--dumpfile`

Dump response data to files. Dir: `./dump_logs/`

- **Type:** `bool`
- **Default:** `False`

- **Example:**

```
--dumpfile
```

### `--bind`

Bind IP. e.g. 127.0.0.1, localhost, 0.0.0.0

- **Type:** `str`
- **Default:** `0.0.0.0`

- **Example:**

```
--bind=127.0.0.1
--bind=192.168.10.1
```

### `--port`

Listen port.

- **Type:** `int`
- **Default:** `8000`

- **Example:**

```
--port=8002
--port=8003
```

### `--timeout`

Timeout. Default: 30.0

- **Type:** `float`
- **Default:** `30.0`

- **Example:**

```
--timeout=60.0
```

### `--restrict_allow`

Restrict except for allowed IP. e.g. 192.168.10.101;192.168.10.0/24

- **Type:** `str`
- **Default:** `None`

- **Example:**

```
--restrict_allow="192.168.2.10;192.168.10.0/24"
```

### `--restrict_deny`

Restrict specified IP. e.g. 192.168.10.101;192.168.10.0/24

- **Type:** `str`
- **Default:** `None`

- **Example:**

```
--restrict_deny="192.168.10.101;192.168.10.102"
```


### `--forwarding`

Enable forwarding and set forwarding destination. Specify TCP forwarding or HTTP forwarding.

- **Type:** `str`
- **Default:** `None`

- **Example:**

```
--forwarding=www.wikipedia.org	# TCP mode
--forwarding=tcp://www.wikipedia.org:80	# TCP mode

--forwarding=http://www.wikipedia.org/ # HTTP mode
--forwarding=https://www.wikipedia.org/ # HTTP mode
```


### `--ssl_context`

SSL context. [SSLv3, TLS1.0, TLS1.1, TLS1.2, TLS1.3]

- **Type:** `str`
- **Default:** `None`
- **Choices:**

| Value  | Description |
|--------|-------------|
| SSLV3  | SSLv3      |
| TLS1.0 | TLS1.0     |
| TLS1.1 | TLS1.1     |
| TLS1.2 | TLS1.2     |
| TLS1.3 | TLS1.3     |

- **Example:**

```
--ssl_context=TLS1.2
```

### `--ssl_keypath`

SSL key path.

- **Type:** `str`
- **Default:** ``

- **Example:**

```
--ssl_keypath=/path/to/keys/
```

### `--ssl_certfile`

SSL certificate file.

- **Type:** `str`
- **Default:** ``

- **Example:**

```
--ssl_certfile=file.cert
```

### `--ssl_keyfile`

SSL key file.

- **Type:** `str`
- **Default:** ``

- **Example:**

```
--ssl_keyfile=file.key
```

### `--http_opt`

Behaviors in HTTP option.

- **Type:** `str`
- **Default:** `INTERACTIVE`
- **Choices:**

| Value       | Description | Related option |
|-------------|-------------|---------------|
| INTERACTIVE | Interactive response.     | -                     |
| FILE        | Display file or directory.      | --http_path, --http_file, --http_file_upload |
| FORWARDING  | Request Forwarding      | --forwarding, --http_forwarding |
| APP      |  Run application or show file.    | --http_path, --http_app |
| INFO        | Display info. It's request headers.   | - |
| PASS        | Pass the display. Mainly used when customizing with Python.    | -            |

- **Example:**

```
--http_opt=FILE
--http_opt=FILE --http_path='../'
--http_opt=APP
--http_opt=APP --http_path='./app/'
--http_opt=FORWARDING --forwarding='http://www.wikipedia.org/'
```

### `--http_path`

HTTP public directory path.

- **Type:** `str`
- **Default:** `./`

- **Example:**

```
--http_path="../"
--http_path="/path"
```

### `--http_digest_auth`

Enable digest authentication. Set authentication setting.

**Formart**

```
- "File": .htdigest
- "User/Raw": "admin2:123456"
- "User/MD5": "admin2:d71fab~~~~dfca14112"
```

- **Type:** `str`
- **Default:** ``

- **Example:**

```
--http_digest_auth="admin:123456"
--http_digest_auth=".htdigest"
```

### `--enable_file_upload`

Enable file-upload in FILE mode. 1: Overwrite 2: New create only

- **Type:** `int`
- **Default:** `0`

- **Example:**

```
--enable_file_upload=1
--enable_file_upload=2
```


### `--version`

Show version information.

- **Type:** `bool`
- **Default:** `False`

## Shortcut options

### `--http_app`

`--http_app` is equivalent to `--mode=HTTP and --http_opt=APP`.

- **Type:** `str`
- **Default:** `None`

- **Example:**

```
--http_app=1 # Current directory
--http_app=./examples/ipserver/
```

### `--http_file`

`--http_file` is equivalent to `--mode=HTTP and --http_opt=FILE`.

- **Type:** `str`
- **Default:** `None`

- **Example:**

```
--http_file=1 # Current directory
--http_file="../"
```

### `--http_file_upload`

`--http_file_upload` is equivalent to `--mode=HTTP and --http_opt=FILE and --enable_file_upload=1`.

- **Type:** `str`
- **Default:** `None`

- **Example:**

```
--http_file_upload=1
--http_file_upload="../"
```

### `--http_forwarding`

`--mode=HTTP and --http_opt=FORWARDING`.

- **Type:** `str`
- **Default:** `None`

- **Example:**

```
--http_forwarding="https://www.amazon.com"
```
