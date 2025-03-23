from ipserver.core.object_factory import ObjectFactory
from ipserver.core.pipeline import Pipeline
from ipserver.ipserver_cmd import IpServerCmd
from string import Template

'''
HTTP customize response.

Command:
# python3 http_response_customize.py --info

http://develop-server:8000/
'''


class MyPipeline(Pipeline):
    def pre_configure(self, args):
        args.mode = 'HTTP'
        args.http_opt = 'PASS'

    def pre_http_respond(self, httpio):
        template = Template('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hello World!</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400..700;1,400..700&display=swap" rel="stylesheet">
    <style>
        body {
            display: flex;
            justify-content: center;
            height: 100vh;
            background-color: #f0f0f0;
            overflow: hidden;
            position: relative;

            font-family: "Lora", serif;
            font-optical-sizing: auto;
            font-weight: 400;
            font-style: normal;
        }
        .message {
            margin-top: 3rem;
        }
        h1 {
            font-size: 4em;
            font-weight: 500;
            animation: colorChange 3s infinite;
        }
        @keyframes colorChange {
            0% { color: red; }
            25% { color: orange; }
            50% { color: yellow; }
            75% { color: green; }
            100% { color: blue; }
        }
        h2 {
            font-size: 1.5em;
            margin-top: 10px;
            color: #333;
            font-weight: normal;
        }
        .confetti {
            position: absolute;
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-bottom: 10px solid;
            opacity: 0.8;
            animation: fall 5s infinite;
        }
        @keyframes fall {
            0% { transform: translateY(0) rotate(0deg); }
            100% { transform: translateY(100vh) rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="message">
        <h1>Hello World!</h1>
        <h2>This is Hello World sample! - HTTP response customize</h2>
        <div>PATH: ${request_path}</div>
        <div>USER_AGENT: ${user_agent}</div>
        <div>REMOTE_IP: ${remote_ip}</div>
    </div>

    <script>
        const colors = ['#ffcc00', '#ff6699', '#66ccff', '#99cc66', '#ffcc66'];
        const createConfetti = () => {
            const confetti = document.createElement('div');
            confetti.classList.add('confetti');
            confetti.style.borderBottomColor = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.left = Math.random() * 100 + 'vw';
            confetti.style.animationDuration = Math.random() * 3 + 5 + 's';

            const rotationSpeed = Math.random() * 2 + 2;
            confetti.style.animation = `fall $${confetti.style.animationDuration} linear infinite, rotate $${rotationSpeed}s linear infinite`;
            confetti.style.animationName = 'fall, rotate';

            document.body.appendChild(confetti);
            setTimeout(() => {
                confetti.remove();
            }, 6000);
        };

        setInterval(createConfetti, 100);
    </script>
</body>
</html>
''')

        httpio.body = template.substitute(
            request_path=httpio.request_path,
            user_agent=httpio.environ['HTTP_USER_AGENT'],
            remote_ip=httpio.environ['REMOTE_ADDR']
        )


class MyObjectFactory(ObjectFactory):
    def create_pipeline(self):
        return MyPipeline()


if __name__ == '__main__':
    factory = MyObjectFactory()

    cmd = IpServerCmd(factory)

    cmd.run()
