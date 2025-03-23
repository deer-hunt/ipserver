'''
[Python execute sample]

$ ipserver --port=8001 --http_app=./examples/public-sample/
URL: http://your-host:8001/examples/public-sample/digest-auth
'''

import time

io = httpio

html = '''<html><head>
<title>This is digest-auth.py</title>
<style>
body {
    padding: 15px;
    margin-bottom: 80px;
    line-height: 13pt;
}

.red {
    color:red;
}
</style>
</head><body>
<h1>This is digest-auth.py</h1>
<br>
'''

# time.sleep(5)

io.print(html)

if io.environ.get('REMOTE_USER'):
    remote_user = io.environ.get('REMOTE_USER')

    html = '''<h2>Digest authentication is enabled</h2>
    <div>Digest authed user: <span class="red">{}</span></div>
    '''.format(remote_user)

    if remote_user == 'admin':
        html += '<br><div>This is admin user\'s privilege.</div>'
    elif remote_user == 'user1' or remote_user == 'user2':
        html += '<br><div>This is general user\'s privilege.</div>'

else:
    html = '''<h2>Digest authentication is disabled</h2>
    <div>Digest authentication is disabled.</div>
    '''.format()

io.print(html)

html = """
<br>
<div>
    <h2>Digest authentication Options:</h2>
    --http_digest_auth=./examples/public-sample/.htdigest<br>
    <br>
    --http_digest_auth=.htdigest<br>
    --http_digest_auth="admin:123456"<br>
    --http_digest_auth="admin:d71fa85bc0ded05215b28dfd8ca14112"<br>
</div>
"""

io.print(html)

io.print('</html>')
