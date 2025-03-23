# Program architecture and Classes

## Modules and Classes and Methods docs.

The following are the documentation for Modules, Classes, and Methods.

- [Module Index](https://deer-hunt.github.io/ipserver/py-modindex.html)
- [Classes and Methods docs](https://deer-hunt.github.io/ipserver/genindex.html)


## Configure and Constant

The following is description of Configure and Constant.

| Class            | Filename           | Description       |
|------------------|-------------------|-------------------|
| [`Config`](https://deer-hunt.github.io/ipserver/modules/ipserver.config.html)         | config.py         | Configure class. There are various configure variables. Example: config_customize.py     |
| `Constant`       | config.py         | Constant class.     |


## ObjectFactory

`ObjectFactory` class provide customizing classes and creating original classes. Important classes are generated in `ObjectFactory`.
If you'd like to create original factory class , extending `ObjectFactory`. And injecting to `IpServerCmd` class.

| Attribute    | Value             |
|----------------------|--------------------------------------------------|
| **Class**     | [ObjectFactory](https://deer-hunt.github.io/ipserver/modules/ipserver.core.object_factory.html)   |
| **Path**     | ./core/object_factory.py   |
| **Example**  | object_factory_original_headers.py   |


## Pipeline

`Pipeline` class provide catching and customizing the data in each processing. `Pipeline` class allows for modifying process behaviors or adding specifications without a lot of class extensions or changing the structure.
It's available to very fine data control.


| Attribute    | Value             |
|----------------------|--------------------------------------------------|
| **Class**     | [Pipeline](https://deer-hunt.github.io/ipserver/modules/ipserver.core.pipeline.html)   |
| **Path**     | ./core/pipeline.py      |
| **Example**    | pipeline_customize.py                  |

**Pipeline's methods**

When Pipeline's methods are dispatched:

**Pipeline's methods**

When Pipeline's methods are dispatched:

| Methods                      | When it dispatch                                            | Processing e.g.                   |
|------------------------------|-------------------------------------------------------------|-----------------------------------|
| `init_configure`             | Initializing arguments values.                              | Customizing arguments and env.    |
| `pre_configure`              | Before configuring arguments.                               | Customizing arguments before configuring. |
| `post_configure`             | After configuring arguments.                                | Customizing arguments after configuring.  |
| `initialize`                 | Initializing with config and socket server.                 | Setting up initial configurations.        |
| `create_socket`              | Creating a socket.                                          | Customizing socket creation.              |
| `connected`                  | When a socket is connected.                                 | Handling socket connection.               |
| `interactive_input`          | Handling interactive input.                                 | Processing interactive commands.          |
| `kick_quiet_interval`                 | When quiet mode is enabled. Call by interval timing.     | Handling quiet mode operations.           |
| `start_listen`               | Starting to listen on a socket.                             | Customizing listening behavior.           |
| `post_accept`                | After accepting a connection.                               | Handling post-accept operations.          |
| `post_receive`               | After receiving data.                                       | Processing received data.                 |
| `complete_receive`           | Completing the receive process.                             | Finalizing received data.                 |
| `pre_send`                   | Before sending data.                                        | Customizing data before sending.          |
| `post_send`                  | After sending data.                                         | Handling post-send operations.            |
| `complete_send`              | Completing the send process.                                | Finalizing sent data.                     |
| `pre_forwarding_send`        | Before forwarding data.                                     | Customizing data before forwarding.       |
| `post_forwarding_receive`    | After receiving forwarded data.                             | Processing forwarded data.                |
| `verify_restriction`         | Verifying connection restrictions.                          | Customizing connection restrictions.      |
| `deny_socket`                | When a socket is denied.                                    | Handling denied socket connections.       |
| `closed_socket_server`       | When a socket server is closed.                             | Handling closed socket server operations.   |
| `closed_socket`              | When a socket is closed.                                    | Handling closed socket connections.       |
| `digest_auth_load`           | Loading digest authentication users.                        | Customizing digest auth user loading.     |
| `digest_auth_verify`         | Verifying digest authentication.                            | Customizing digest auth verification.     |
| `pre_http_process`           | Before processing an HTTP request.                          | Customizing HTTP request processing.      |
| `get_http_app_path`          | Getting the HTTP app path.                                  | Customizing HTTP app path resolution.     |
| `is_enable_file_upload`      | Checking if file upload is enabled.                         | Customizing file upload enablement.       |
| `pre_http_forwarding_request`| Before forwarding an HTTP request.                  | Customizing HTTP forwarding request.      |
| `post_http_forwarding_request`| After forwarding an HTTP request.                    | Processing forwarded HTTP request.        |
| `pre_http_file_upload`       | Before uploading an file in HTTP mode.                  | Customizing HTTP file upload.             |
| `post_http_file_upload`      | After uploading an file in HTTP mode.                    | Handling post-upload operations.          |
| `pre_http_respond`           | Before responding to an HTTP request.                   | Customizing HTTP response.                |
| `get_filename`               | Getting the filename for a connection.                      | Customizing filename resolution.          |
| `pre_dump_write`              | Before writing to a file.                                   | Customizing file write operations.        |
| `complete`                   | After completing all processes.                             | Final processing.                         |


## Utils

In `./util`, there are some util classes. Those are used in various places.

| Path                      | Classes                     |
|----------------------|--------------------------------------------------|
| ./util/args_util.py      | `ArgValidator`, `StdinLoader` |
| ./util/requester.py    | `Requester`        |
| ./util/socket_client.py       | `SocketClient`    |
| ./util/urlparser.py       | `URLParser`    |


## Debugging

This description is description of development and debugging related `ipserver`.

## Program specification

| **Item**          | **Description**            |
|-------------------|-----------------------|
| **Python version**| 3.6 or later. * |
| **Dependencies**   | multipart              |


## Debugging

You can see detailed debug information by specifying `--verbose=3` or `--debug`. In detail, please read `--verbose` option.

```bash
$ ipserver ***** --verbose=2    #INFO
$ ipserver ***** --verbose=3    #DEBUG

$ ipserver ***** --info     #INFO  This option is equivalent to "--verbose=2"

$ ipserver ***** --debug     #DEBUG  This option is equivalent to "--verbose=3"
```


### Log sample and description

The following is debugging log with each comments.


## Customize Examples

There are examples of program customization. Please refer to [here](./customize_examples.md).



## Not support Python 2.7 ?

"ipserver" doesn't support Python 2.7. However "ipserver" has been developed to avoid using the latest Python specifications as much as possible, So you can refactor to Python 2.7 code easily.

**Refactoring points**

- ABC module
- http.client module
- urllib module

> And any other few modules.

