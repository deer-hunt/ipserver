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

Enable logging. Set Log filename. Verbose data is written.
If `--verbose` is 0, `--verbose` is changed to 2 automatically. 

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

Load arguments from conf file by JSON. e.g. ipserver_conf.json
JSON data is shown in `--info, --verbose=2` log.

- **Type:** `str`
- **Default:** `None`

- **Example:**

```
# ipserver --conf=ipserver_conf.json
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
- **Default:** 2048
- **Choices:**

- **Example:**

```
--output_max=100000
```

### `--dumpfile`

Dump response data to files. Dir: `./dumpfiles/`

- **Type:** `bool`
- **Default:** `False`

- **Example:**

```
--dumpfile
```

**Dumpfile examples:**

```
ipserver_9_1_recv_192.168.10.3_58395.dat
ipserver_8_1_recv_192.168.10.3_58385.dat
ipserver_7_1_recv_192.168.10.3_58384.dat
ipserver_6_4_send_192.168.10.3_58442.dat
ipserver_6_3_recv_192.168.10.3_58442.dat
ipserver_6_2_send_192.168.10.3_58442.dat
ipserver_6_1_recv_192.168.10.3_58442.dat
ipserver_5_1_recv_192.168.10.3_58441.dat
ipserver_5_1_recv_192.168.10.3_58362.dat
ipserver_4_1_recv_192.168.10.3_58355.dat
ipserver_3_4_send_192.168.10.3_58426.dat
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

### `--connection_max`

Max connections. If the limit is reached, waiting until there is availability.

- **Type:** `int`
- **Default:** `20`

- **Example:**

```
--connection_max=20
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

**In TCP mode**

```
--forwarding=www.wikipedia.org	 # TCP connection
--forwarding=tcp://www.wikipedia.org:80 # TCP connection
--forwarding=ssl://www.wikipedia.org:80 # SSL connection
```

**In HTTP mode**

```
--forwarding=http://www.wikipedia.org/ # HTTP reuqest
--forwarding=https://www.wikipedia.org/ # HTTPS request
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

### `--http_forwarding_convert_host`

Convert hostname of content to `/` in HTTP forwarding. This feature provide that the resource file as "css, js, img" to be loaded through `ipserver` forcibly.

**Behavior:**

```
<img src="https://www.github.com/hello">, <img src="http://github.com/hello">
 ↓
<img src="/hello">
```

- **Type:** `bool`
- **Default:** `False`

- **Example:**

```
--http_forwarding_convert_host
ipserver --http_forwarding="https://www.amazon.com/" --http_forwarding_convert_host --info
```

### `--http_digest_auth`

Enable digest authentication. Set authentication setting.

**Format**

```
a. "Filename": .htdigest
b. "User/Password": "admin2:123456"
c. "User/MD5": "admin2:d71fab~~~~dfca14112"
```

- **Type:** `str`
- **Default:** ``

- **Example:**

```
--http_digest_auth="admin:123456"
--http_digest_auth=".htdigest"
```

**How to create .htdigest file**

```
$ htdigest -c .htdigest "digest" admin

--
admin:digest:09b62d36d2639b4431bef96221975aed
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
