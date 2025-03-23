'''
[Python execute sample]

$ ipserver --port=8001 --http_app=./examples/public-sample/
URL: http://your-host:8001/examples/public-sample/file-upload?abc=1234
'''

import time
import os

io = httpio

# flake8: ignore F821

html = '''<html><head>
<title>This is file-upload.py</title>
<style>
body {
    padding: 15px;
    margin-bottom: 80px;
    line-height: 13pt;
}

.uploaded {
    color: red;
    margin-top: 10px;
}
</style>
</head><body>
<h1>This is file-upload.py</h1>
<br>
'''

io.print(html)

html = '''<h2>Environ</h2>
<textarea cols=120 rows=8>
{}
</textarea>'''.format(io.environ)

io.print(html)

html = '''<h2>GET/POST Parameters</h2>
<pre>
GET: {}
POST: {}
</pre>'''.format(io.gets, io.posts)

io.print(html)

html = '''<h2>File</h2>
<form action="?" method="post" enctype="multipart/form-data">
    <table>
        <tr>
            <td>TEXT:</td>
            <td><input type="text" name="text1"></td>
        </tr>
        <tr>
            <td>FILE1:</td>
            <td><input type="file" name="file1"></td>
        </tr>
        <tr>
            <td>FILE2:</td>
            <td><input type="file" name="file2"></td>
        </tr>
        <tr>
            <td colspan="2" style="text-align: right;padding-top: 10px;">
                <button type="submit">Upload</button>
            </td>
        </tr>
    </table>
</form>
'''

io.print(html)


def save_file(name):
    done = False

    if name in io.posts:
        f = io.posts[name]

        if f:
            dir = './files/'

            os.makedirs(dir, exist_ok=True)

            with open(dir + f.filename, 'wb') as file:
                file.write(f.file.read())
                done = True

    return done


if io.posts:
    v1 = save_file('file1')
    v2 = save_file('file2')

    if v1 or v2:
        io.print('<div class="uploaded">File is uploaded.(./files/)</div>')

io.print('</html>')
