# IpServer

<div>

<a href="https://github.com/deer-hunt/ipserver/actions/workflows/unit-tests.yml"><img alt="CI - Test" src="https://github.com/deer-hunt/ipserver/actions/workflows/unit-tests.yml/badge.svg"></a>
<a href="https://github.com/deer-hunt/ipserver/actions/workflows/unit-tests-windows.yml"><img alt="CI - Test" src="https://github.com/deer-hunt/ipserver/actions/workflows/unit-tests-windows.yml/badge.svg"></a>
<a href="https://github.com/deer-hunt/ipserver/actions/workflows/unit-tests-macos.yml"><img alt="CI - Test" src="https://github.com/deer-hunt/ipserver/actions/workflows/unit-tests-macos.yml/badge.svg"></a>
<img alt="PyPI - Status" src="https://img.shields.io/pypi/status/ipserver">
<a href="https://github.com/deer-hunt/ipserver/blob/main/LICENSE.md"><img alt="License - MIT" src="https://img.shields.io/pypi/l/ipserver.svg"></a>
<a href="https://pypi.org/project/ipserver/"><img alt="Newest PyPI version" src="https://img.shields.io/pypi/v/ipserver.svg"></a>
<a href="https://pypi.org/project/ipserver/"><img alt="Number of PyPI downloads" src="https://img.shields.io/pypi/dm/ipserver.svg"></a>
<img alt="GitHub code size in bytes" src="https://img.shields.io/github/languages/code-size/deer-hunt/ipserver">
<a href="https://pypi.org/project/ipserver"><img alt="Supported Versions" src="https://img.shields.io/pypi/pyversions/ipserver.svg"></a>
<a href="https://deer-hunt.github.io/ipserver/" alt="ipserver's documentation site"><img src="https://img.shields.io/badge/stable%20docs-github.io-brightgreen?style=flat&color=%2373DC8C&label=Docs"/></a>

</div>

<div>
<img width="80" height="80" src="https://raw.githubusercontent.com/deer-hunt/ipserver/main/docs/images/ipsurv-logo.png" align="left" />

"ipserver" is a simple server that supports TCP, UDP, SSL, HTTP, and HTTPS protocols for various uses such as testing, debugging, or network investigation. It features also an interactive mode and forwarding capabilities. Additionally, you can customize its behavior using Python.

</div>

<br>
<img src="https://raw.githubusercontent.com/deer-hunt/ipserver/main/docs/images/ipserver-thumbs.png" alt="ipserver visual image" />

## Installation

**PyPI**

```bash
$ pip install ipserver
or
$ pip3 install ipserver
```

```
$ ipserver --help
```

**Conda**

Coming soon..


## Requirements

- ```python``` and ```pip``` command
- Python 3.6 or later version.

## Documentation site

Coming soon...


## Features

- Simple TCP / UDP server.
- Support SSL.
- HTTP / HTTPS server.
- IP restriction.
- Interactive sending.
- TCP Forwarding.
- Display received data or sent data in various format(TEXT, BINARY, BASE64, HEX...).
- HTTP -> FORWARDING: Forwarding HTTP communication. e.g. HTTP <-> HTTPS
- HTTP -> FILE: Viewing file and directory and uploading file.
- HTTP -> APP: Running python application. And Running CGI via python.
- HTTP -> INFO: Show request headers from client. 
- Support HTTP digest authentication.
- Logging / Data dump File.
- Configure by JSON file.
- Customize by Python code. e.g. You can convert transmission data or develop original protocol server.


## Running example

```bash
$ ipserver --port=8002 --mode=HTTP
Mode:         HTTP
Listen:       0.0.0.0
Port:         8002
HTTP opt:     FILE
Input:        TEXT
Output:       NONE
Timeout:      30.0

[Command help]
send:         Begin input to send. Send by a Line-break. The shortcut is `s`.
bulk:         Begin bulk input to send. Send by Ctrl-key. The shortcut is `b`.
"1,2,3,..":   Switch the connection.
current:      Show current connection.
latest:       Switch latest connection.
list:         List the connections.
close:        Close current connection.
refresh:      Refresh connections.
exit:         Exit.
help:         Show help.

:
[1] Accepted from 192.168.10.1:52322

[1] Closed from 192.168.10.1:52322

[2] Accepted from 192.168.10.1:52329

[2] Receive 600 bytes from 192.168.10.1:52329

[2] Send 421 bytes to 192.168.10.1:52329

[3] Accepted from 192.168.10.1:52330
```

## Description of Mode

### TCP Server

**Simple server**

```bash
$ ipserver --port=8002
$ ipserver --port=8002 --mode=TCP --bind=127.0.0.1
$ ipserver --port=8002 --timeout=120

$ ipserver --port=8002 --info
$ ipserver --port=8002 --debug
$ ipserver --port=8002 --log=app.log

$ ipserver --port=8002 --quiet
```

```
# TEST
# telnet localhost 8002
```

**SSL server**

```bash
$ ipserver --port=8443 --mode=SSL
$ ipserver --port=8443 --mode=SSL --ssl_context=TLS1.1
$ ipserver --port=8443 --mode=SSL --ssl_keypath=/home/foo/sslkeys/
```

```bash
# TEST
$ openssl s_client -connect 192.168.1.100:8443
```


**IP restriction**

```bash
$ ipserver --port=8002 --restrict_allow=192.168.2.10
$ ipserver --port=8002 --restrict_allow="192.168.2.10;192.168.10.0/24"

$ ipserver --port=8002 --restrict_deny=192.168.10.101
$ ipserver --port=8002 --restrict_deny="192.168.10.101;192.168.50.0/24"
```

**Dump file**

```bash
$ ipserver --port=8002 --dumpfile
```

### TCP Forwarding

```
$ ipserver --port=8002 --forwarding=wikipedia.org:80
$ ipserver --port=8443 --mode=SSL --forwarding=tcp://wikipedia.org:80
$ ipserver --port=8002 --forwarding=ssl://wikipedia.org:443
$ ipserver --port=8002 --forwarding=wikipedia.org:80 --dumpfile
```

```bash
# TEST
$ openssl s_client -connect 192.168.1.100:8443

$ curl https://localhost/path -v
```

> Please see the following about "HTTP Forwarding".

### HTTP/HTTPS

**View File and directory**

```bash
$ ipserver --port=8002 --mode=HTTP
$ ipserver --port=8002 --mode=HTTP --http_opt=FILE
$ ipserver --port=8002 --mode=HTTP --http_opt=FILE --http_path="../"

$ ipserver --port=8443 --mode=HTTPS
$ ipserver --port=8443 --mode=HTTPS --http_path="../"

# Shortcut
$ ipserver --port=8002 --http_file=1
$ ipserver --port=8002 --http_file="../"
```

**Enable file upload**

```bash
$ ipserver --port=8002 --mode=HTTP --http_opt=FILE --enable_file_upload=1
$ ipserver --port=8002 --mode=HTTPS --http_path="../" --enable_file_upload=2

# Shortcut
$ ipserver --port=8002 --http_file_upload=1
$ ipserver --port=8002 --http_file_upload="../"
```

**Application**

```bash
$ ipserver --port=8002 --mode=HTTP --http_opt=APP
$ ipserver --port=8002 --mode=HTTPS--http_opt=APP --http_path="../"

# Shortcut
$ ipserver --port=8002 --http_app=1
$ ipserver --port=8002 --http_app="./app/"
```

**Display info**

```bash
$ ipserver --port=8002 --mode=HTTP --http_opt=INFO
```

**HTTP Forwarding**

```bash
$ ipserver --port=8002 --mode=HTTP --http_opt=FORWARDING --forwarding="https://www.reddit.com/"

# Shortcut
$ ipserver --port=8002 --http_forwarding="https://www.reddit.com/"
$ ipserver --port=8002 --mode=HTTPS --http_forwarding="https://www.wikipedia.org/"
```

**HTTP/HTTPS test**

You can test by web-browser or command.

```bash
# Commands
$ curl http://localhost/test.py

$ curl https://localhost:8443 -k -v
```

## HTTP Digest authentication

```bash
$ ipserver --port=8002 --mode=HTTP --http_digest_auth="admin:123456"
$ ipserver --port=8002 --mode=HTTP --http_digest_auth="admin:d71fa85bc0ded05215b28dfd8ca14112" --http_file_upload=1

$ ipserver --port=8002 --http_app="./app/" --http_digest_auth=".htdigest"
$ ipserver --port=8443 --mode=HTTPS --http_app="./app/" --http_digest_auth=".htdigest"
```

## Mixed options

**HTTP file-upload + IP restriction**

```
$ ipserver --port=8002 --http_file_upload="../" --restrict_allow="192.168.2.10;192.168.10.0/24"
```

**HTTP application + Digest auth**

```
$ ipserver --port=8002 --http_app="./app/" --http_digest_auth="admin:123456"
```

**HTTPS + info + dump**

```
$ ipserver --port=8002 --mode=HTTPS --http_opt=INFO --dumpfile
```


## Description of Interactive command

```
:help
[Command help]
send:         Begin input to send. Send by a Line-break. The shortcut is `s`.
bulk:         Begin bulk input to send. Send by Ctrl-key. The shortcut is `b`.
"1,2,3,..":   Switch the connection.
current:      Show current connection.
latest:       Switch latest connection.
list:         List the connections.
close:        Close current connection.
refresh:      Refresh connections.
exit:         Exit.
help:         Show help.
```

**Examples**

```
:s
[1] Switched automatically.
Please input data to send...

Hello world!

[1] Sent to 127.0.0.1:45528

--
:2
[2] Switched.

--
:list
[1] 192.168.10.1:54721
[2] 192.168.10.1:54722

--
:latest
[2] Switched automatically.

--
:current

[2] Switched automatically.
ID: 2
Client IP: 192.168.10.1
Client port: 54722

--
:close
[2] Switched automatically.
[2] The connection is closed.
```


### Command options

```ipserver``` have many options. Please read [Command arguments(.md) reference](https://github.com/deer-hunt/ipserver/blob/main/docs/command_arguments.md).

```
usage: ipserver [-h] [--verbose {0,1,2,3}] [--debug] [--info]
                   [--log {string}] [--quiet] [--conf]
                   [--mode {TCP,UDP,SSL,HTTP,HTTPS}]
                   [--input {TEXT,BINARY,HEX,BASE64}]
                   [--output {NONE,TEXT,BINARY,HEX,BASE64}]
                   [--output_target {ALL,SEND,RECEIVE}] [--output_max]
                   [--bind {string}] [--port {int}] [--timeout {float}]
                   [--dumpfile]
                   [--restrict_allow {string}]
                   [--restrict_deny {string}]
                   [--ssl_context {SSLV3,TLS1.0,TLS1.1,TLS1.2,TLS1.3}]
                   [--ssl_keypath {string}] [--ssl_certfile {string}]
                   [--ssl_keyfile {string}] [--forwarding {string}]
                   [--http_opt {INTERACTIVE,FILE,PASS,APP,INFO,FORWARDING}]
                   [--http_path {string}] [--http_digest_auth {string}]
                   [--enable_file_upload {int}] [--http_app {string}]
                   [--http_file {string}] [--http_file_upload {string}]
                   [--http_forwarding {string}] [--version]
```

## Path summary

| Directory        | Description                                         |
|-----------------------|-----------------------------------------------------|
| `.github`            | GitHub Actions files          |
| `docs`               | Documentation files                                 |
| `examples`           | Customizing program examples                 |
| `examples/public-sample`           | Sample public files                 |
| `ipserver`             | Main package/Sources                            |
| `tests`              | Test files                     |

## Documents

The following documents exist in `ipsurv`. You can read documents in [Documentation site](https://deer-hunt.github.io/ipsurv/).

| Title                       | Path                                                                                                                             |
|-------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| **Command arguments**    | [command_arguments.md](https://deer-hunt.github.io/ipserver/pages/command_arguments.html)                       |
| **Customizing and Examples**       | [customize_examples.md](https://deer-hunt.github.io/ipserver/pages/customize_examples.html)                     |
| **Development and Architecture**    | [development_architecture.md](https://github.com/deer-hunt/ipserver/blob/main/docs/development_architecture.md)      |
| **ipserver's Major Modules and Classes** | Coming soon.                                 |


## Debugging

In verbose mode, outputting internal data and behaviors in detail.

```bash
$ ipserver ***** --verbose=2    #INFO
$ ipserver ***** --verbose=3    #DEBUG

$ ipserver ***** --info     #INFO  This option is equivalent to "--verbose=2"

$ ipserver ***** --debug     #DEBUG  This option is equivalent to "--verbose=3"
```


## Dependencies

- [multipart](https://pypi.org/project/multipart/)

