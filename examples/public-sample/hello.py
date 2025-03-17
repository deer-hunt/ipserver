'''
[Python execute sample]

$ ipserver --port=8001 --http_app=./examples/ipserver-sample/
'''

html = '''<html><head>
<title>This is hello.py</title>
<style>
body {
    padding: 15px;
    margin-bottom: 80px;
    line-height: 18pt;
}
</style>
</head><body>
<h1>This is hello.py</h1>
'''

httpio.print(html)

httpio.print('<h2>Hello world!</h2>')

for i in range(10):
    httpio.print('<div>{}. Hello world!</div>'.format(i))

httpio.print('</html>')
