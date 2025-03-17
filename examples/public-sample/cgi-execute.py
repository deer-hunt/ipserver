'''
[CGI execute sample]

Require to change permission.

$ chmod a+x shell-sample.sh

$ ipserver --port=8001 --http_app=./examples/ipserver-sample/
URL: http://your-host:8001/examples/ipserver/cgi-execute
'''

import time
import subprocess

io = httpio # noqa

html = '''<html><head>
<title>This is CGI execute sample</title>
<style>
body {
    padding: 15px;
    margin-bottom: 80px;
    line-height: 13pt;
}
</style>
</head><body>
<h1>This is CGI execute sample</h1>
<br>
'''

io.print(html)

script_path = io.directory_path + 'programs/shell-sample.sh'

result = subprocess.run([script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

io.print('<pre>' + result.stdout + '</pre>')

io.print('</html>')
