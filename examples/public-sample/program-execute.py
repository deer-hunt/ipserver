'''
[Program execute sample]

Require to change permission.

$ chmod a+x shell-sample.sh

$ ipserver --port=8001 --http_app=./examples/ipserver-sample/
URL: http://your-host:8001/examples/ipserver/program-execute
'''

import subprocess

is_execute = True

program = 'php'

if is_execute:
    programs = {
        'php': (['php'], 'sample.php'),
        'ruby': (['ruby'], 'sample.rb'),
        'js': (['node'], 'sample.js'),
        'go': (['go', 'run'], 'sample.go'),
        'perl': (['perl'], 'sample.pl'),
    }

    (scripts, sample_file) = programs[program]

    io = httpio

    html = '''<html><head>
    <title>This is Program execute sample</title>
    <style>
    body {
        padding: 15px;
        margin-bottom: 80px;
        line-height: 13pt;
    }
    </style>
    </head><body>
    <h1>This is Program execute sample</h1>
    <br>
    '''

    httpio.print(html)

    script_path = httpio.directory_path + 'programs/' + sample_file

    scripts.append(script_path)

    result = subprocess.run(scripts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    httpio.print('<pre>' + result.stdout + '</pre>')

    httpio.print('</html>')
else:
    httpio.print('Safety reject! ("is_execute" is False)')
