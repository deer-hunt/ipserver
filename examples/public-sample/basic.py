'''
[Python execute sample]

$ ipserver --port=8001 --http_app=./examples/public-sample/
URL: http://your-host:8001/examples/public-sample/basic.py?abc=1234
'''

import time

io = httpio # noqa

html = '''<html><head>
<title>This is python-sample.py</title>
<style>
body {
    padding: 15px;
    margin-bottom: 80px;
    line-height: 13pt;
}
</style>
</head><body>
<h1>This is python-sample.py</h1>
<br>
'''

# time.sleep(5)

io.print(html)

html = '''<h2>GET/POST Parameters</h2>
<pre>
GET: {}
POST: {}
</pre>'''.format(io.gets, io.posts)

io.print(html)

io.print('<h2>Headers</h2>')
io.print('<pre>')
io.print('Method: ' + io.method)
io.print(io.req_headers)
io.print('</pre>')

# Shared object
if 'a' not in shared_object:
    shared_object['a'] = 0
    shared_object['b'] = 0

shared_object['a'] += 1
shared_object['b'] += 2

html = '''<h2>Shared object</h2>
<div>a: {a}</div>
<div>b: {b}</div>
'''.format(**shared_object)

io.print(html)

html = '''<h2>Internal Info</h2>
<div>conn_id: {}</div>
'''.format(conn_sock.conn_id)

io.print(html)

html = '''<h2>Environ</h2>
<textarea cols=120 rows=8>
{}
</textarea>'''.format(io.environ)

io.print(html)

html = '''<h2>Send POST</h2>
<form method='POST' action='?abc=123'>
<div><input name='xyz' type='text' value='' placeholder='value...'></div><br>

<input type='submit' value='POST sample'>
</form>
'''

io.print(html)

io.print('</html>')
