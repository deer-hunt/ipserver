# Customizing and Examples

## Overview

```ipserver``` is implemented as customizable program architecture. It provide extending features and several classes.

## HTTP public sample files

There are some sample files for HTTP mode.

Path: [../examples/public-sample](examples/public-sample)

**Run application**

```
$ ipserver --port=8002 --http_app="/path/to/examples/public-sample/"
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
$ ipserver --port=8002 --http_file="/path/to/examples/public-sample/"
```

**Use Digest auth**

```
$ ipserver --port=8002 --http_file=1 --http_digest_auth="/path/to/examples/public-sample/.htdigest"
```


## Example programs of Server

There are several example programs of how to customize. Please refer to the comments in each program for more details.

**Path:** [``./examples/``](https://github.com/deer-hunt/ipserver/tree/main/examples)


| Program                          | Description                                      |
|----------------------------------|--------------------------------------------------|
| ./public-sample/            | Sample public files.                      |
| config_customize.py           | Customizing config.                      |
| pipeline_customize.py            | Customizing Pipeline class.                      |
| original_protocol.py             | Implementing a custom protocol for calculations. |
| inject_original_class.py         | Injecting original class object.                 |
| http_url_routing.py              | Implementing URL routing.                        |
| http_upload_filtering.py         | Filtering file uploads.                          |
| http_response_customize.py       | Customizing HTTP responses.                      |
| http_opt_by_path.py              | Setting HTTP options based on the request path.   |
| http_forwarding_html_append.py   | Appending HTML content to forwarded responses.   |
| http_dummy_response.py           | Generating dummy HTTP responses.                 |
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
