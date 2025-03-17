# Command arguments

This document is a description of ipserver's command arguments.

## General and Debugging

### `--verbose`

Verbose mode. Level - 1:TRACE_ERROR, 2:INFO, 3:DEBUG.

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
- **Action:** `store_true`

- **Example:**

```
--debug
```

### `--log`

Verbose log filename.

- **Type:** `str`
- **Default:** `None`
- **Metavar:** `{string}`

- **Example:**

```
--log=logfile.txt
```

### `--quiet`

Hide to output message.

- **Type:** `bool`
- **Default:** `False`
- **Action:** `store_true`

- **Example:**

```
--quiet
```

### `--conf`

Load arguments from conf file by JSON. e.g.: ipserver.json

- **Type:** `str`
- **Default:** `None`
- **Metavar:** `{string}`

- **Example:**

```
--conf=ipserver.json
```

## Main Arguments

### `--mode`

Listening mode. Default: TCP

- **Type:** `str.upper`
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
```

### `--input`

Input format. Default: TEXT

- **Type:** `str.upper`
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

- **Type:** `str.upper`
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
```

### `--bind`

Bind IP. e.g. 127.0.0.1, localhost, 0.0.0.0

- **Type:** `str`
- **Default:** `0.0.0.0`
- **Metavar:** `{string}`

- **Example:**

```
--bind=127.0.0.1
```

### `--port`

Listen port.

- **Type:** `int`
- **Default:** `0`
- **Metavar:** `{int}`

- **Example:**

```
--port=8000
--port=8001
```

### `--timeout`

Timeout. Default: 30.0

- **Type:** `float`
- **Default:** `30.0`
- **Metavar:** `{float}`

- **Example:**

```
--timeout=60.0
```

### `--dumpfile`

Dump response data to files. Dir: `./dump_logs/`

- **Type:** `bool`
- **Default:** `False`
- **Action:** `store_true`

- **Example:**

```
--dumpfile
```

### `--ssl_context`

SSL context. [SSLv3, TLS1.0, TLS1.1, TLS1.2, TLS1.3]

- **Type:** `str.upper`
- **Default:** `None`
- **Choices:**

| Value  | Description |
|--------|-------------|
| SSLV3  |             |
| TLS1.0 |             |
| TLS1.1 |             |
| TLS1.2 |             |
| TLS1.3 |             |

- **Example:**

```
--ssl_context=TLS1.2
```

### `--ssl_keypath`

SSL key path.

- **Type:** `str`
- **Default:** ``
- **Metavar:** `{string}`

- **Example:**

```
--ssl_keypath=path/to/key
```

### `--ssl_certfile`

SSL certificate file.

- **Type:** `str`
- **Default:** ``
- **Metavar:** `{string}`

- **Example:**

```
--ssl_certfile=path/to/cert
```

### `--ssl_keyfile`

SSL key file.

- **Type:** `str`
- **Default:** ``
- **Metavar:** `{string}`

- **Example:**

```
--ssl_keyfile=path/to/keyfile
```

### `--http_opt`

Behaviors in HTTP option.

- **Type:** `str.upper`
- **Default:** `INTERACTIVE`
- **Choices:**

| Value       | Description |
|-------------|-------------|
| INTERACTIVE |             |
| FILE        |             |
| PASS        |             |
| APP      |             |
| INFO        |             |
| FORWARDING  |             |

- **Example:**

```
--http_opt=FILE
```

### `--http_path`

HTTP path.

- **Type:** `str`
- **Default:** `./`
- **Metavar:** `{string}`

- **Example:**

```
--http_path=./path
```

### `--forwarding`

Forwarding destination.

- **Type:** `str`
- **Default:** `None`
- **Metavar:** `{string}`

- **Example:**

```
--forwarding=http://example.com
```

### `--http_app`

`--http_app` is equivalent to `--mode=HTTP and --http_opt=APP`.

- **Type:** `str`
- **Default:** `False`
- **Metavar:** `{string}`
- **Group:** `shortcut`

- **Example:**

```
--http_app=1 # Current directory
--http_app=./examples/ipserver/
```

### `--http_file`

`--http_file` is equivalent to `--mode=HTTP and --http_opt=FILE`.

- **Type:** `str`
- **Default:** `False`
- **Metavar:** `{string}`
- **Group:** `shortcut`

- **Example:**

```
--http_file=1 # Current directory
--http_file=./
```

### `--http_forwarding`

`--mode=HTTP and --http_opt=FORWARDING`.

- **Type:** `str`
- **Default:** `False`
- **Metavar:** `{string}`
- **Group:** `shortcut`

- **Example:**

```
--http_forwarding=https://www.amazon.com
```

### `--version`

Show version information.

- **Type:** `bool`
- **Default:** `False`
- **Action:** `store_true`

