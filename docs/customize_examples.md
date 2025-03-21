# Customizing and Examples

## Overview

```ipserver``` is implemented as customizable program architecture. It provide extending features and several classes.

## HTTP public sample files

There are some sample files for HTTP mode.

Path: [../examples/public-sample](examples/public-sample)

**Run application**

```
$ ipserver --http_app="/path/to/examples/public-sample/"
```

**Result by browser**

```
This is Sample Index

Static
   Hello world!
   SVG sample

Application
  hello.py
  basic.py
  digest-auth.py
  image-output.py
  file-upload.py
  cgi-execute.py
  program-execute.py
    programs/
```

**Display file and directory**

```
$ ipserver --http_file="/path/to/examples/public-sample/"
```

**Use Digest auth**

```
$ ipserver --http_file=1 --http_digest_auth="admin:12345678"
$ ipserver --http_file=1 --http_digest_auth="/path/to/examples/public-sample/.htdigest"
```


## Example programs of Server

There are several example programs of how to customize. Please refer to the comments in each program for more details.

**Path:** [``./examples/``](https://github.com/deer-hunt/ipserver/tree/main/examples)


| Program                          | Description                                      |
|----------------------------------|--------------------------------------------------|
| ./public-sample/            | Sample public files. There are various sample files, including a sample .htdigest file fro HTTP mode test.                 |
| config_customize.py           | Customizing config.                      |
| pipeline_customize.py            | Customizing Pipeline class.                      |
| original_protocol.py             | Implementing a custom protocol for calculations. |
| inject_original_class.py         | Injecting original class object.                 |
| tcp_raw_http_response.py           | Response HTTP by raw data.            |
| tcp_forwarding_change_data.py        | TCP forwarding. Changing transmission data.        |
| tcp_forwarding_ssl_protocol.py        | The forwarding protocol is SSL, however the listening protocol is not SSL. So you can debug the transmission data in detail.         
| benchmark_download_speed.py        | Benchmark transfer speed by downloading dummy image. e.g. `http://develop-server:8002/bench?mb=250`         |
| http_url_routing.py              | Implementing URL routing in HTTP mode.                |
| http_upload_filtering.py         | Filtering file uploads and set filename.                    |
| http_response_customize.py       | Customizing HTTP responses.                      |
| http_opt_by_path.py              | Setting `http_opt` by path. Changing the behavior.  |
| http_forwarding_change_header.py | Changing request header in HTTP forwarding. Set random Accept-Language. Forwarding-request is HTTPS request, But the protocol listened on HTTP, So you can change HTTP header.|
| http_forwarding_html_append.py   | Appending HTML content in HTTP forwarding. `Content-length` is changed automatically in HTTP mode. |
| customize_http_handler.py        | Customizing the HTTP handler.                    |


## Execution examples

### original_protocol.py

**Server**

```bash
$ python original_protocol.py --port=8001

~~~~~~

[1] Accepted from 127.0.0.1:40662

[1] Send 35 bytes to 127.0.0.1:40662

[1] Receive 5 bytes from 127.0.0.1:40662
1+3


[1] Send 11 bytes to 127.0.0.1:40662

[1] Receive 7 bytes from 127.0.0.1:40662
8*9*2

```

**Client**

```bash
-bash-4.2$ telnet localhost 8001
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.

Welcome to Calculation protocol.

1+3
ANSWER: 4

8*9*2
ANSWER: 144
```


### http_response_customize.py

**Server**

```bash
$ python http_response_customize.py --port=8001

~~~~
```

**Browser**

URL http://192.168.10.100:8001/


```
Hello World!

This is Hello World sample! - HTTP response customize

PATH: /
USER_AGENT: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36
REMOTE_IP: 192.168.10.5
```
