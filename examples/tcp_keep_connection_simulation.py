import math
import random
import re
import threading
import time
from datetime import datetime
from urllib.parse import parse_qs

import matplotlib.pyplot as plt

from ipserver.core.object_factory import ObjectFactory
from ipserver.core.pipeline import Pipeline
from ipserver.ipserver_cmd import IpServerCmd
from ipserver.util.sys_util import Output

'''
Keep connection & Particle simulation. Run command to Particle simulation via TCP protocol.

# python3 tcp_raw_http_response.py --port=8002
# telnet develop-server 8002

[Command]
DATE
GETPOS;id=1
PLAYPOS;id=1
PLAYPOS;id=1&num=50
SAVEIMG
'''


class MyPipeline(Pipeline):
    def __init__(self):
        super().__init__()

        self.simulation = ParticleSimulation(num_particles=20, width=1000, height=1000)

    def pre_configure(self, args):
        args.mode = 'TCP'
        args.timeout = -1
        args.quiet = 2

        self._start_simulation()

        Output.warn('Keep connection & simple protocol.\n\n')

    def _start_simulation(self):
        thread = threading.Thread(target=self.simulation.update_particles)
        thread.start()

    def post_accept(self, conn_sock, conn_bucket):
        response = '\nKeep connection & simple protocol.\n\n'

        conn_sock.send_queue(response.encode())

    def complete_receive(self, conn_sock, binary, send_binary=None):
        command, params = self._parse_command_params(binary)

        response = self._run_command(conn_sock, command, params)

        Output.line(command + ';' + response)

        response = response + '\n'
        response = response.encode()

        return response

    def kick_quiet_interval(self, conn_bucket):
        con_socks = conn_bucket.get_conns()

        for con_sock in con_socks:
            data = 'PING;{}\n'.format(int(time.time()))
            con_sock.send_queue(data.encode())

    def _run_command(self, conn_sock, command, params):
        response = None

        if command == 'HELLO':
            response = 'OK'
        elif command == 'DATE':
            response = str(datetime.now())
        elif command == 'GETPOS':
            response = self._get_particle_pos(params)
        elif command == 'PLAYPOS':
            num = int(params.get('num', 10))

            for i in range(num):
                result = self._get_particle_pos(params) + '\n'
                conn_sock.send_queue(result.encode())
                time.sleep(0.5)

            response = 'COMPLETE'
        elif command == 'SAVEIMG':
            response = self.simulation.save_png()
        else:
            response = 'UNKNOWN'

        return response

    def _get_particle_pos(self, params):
        particle = self.simulation.get_particle(params.get('id'))

        if particle:
            response = str(particle.position())
        else:
            response = 'UNKNOWN ID'

        return response

    def _parse_command_params(self, binary):
        line = binary.decode()

        parts = re.split(r';', line, maxsplit=1)

        if len(parts) > 1:
            command, params_value = parts
            parsed = parse_qs(params_value)
            params = {key: value[0] for key, value in parsed.items()}
        else:
            command = parts[0]
            params = {}

        command = command.upper().strip()

        return command, params

    def pre_send(self, conn_sock, binary):
        return binary


class MyObjectFactory(ObjectFactory):
    def create_pipeline(self):
        return MyPipeline()


class Particle:
    def __init__(self, id, x, y, speed):
        self.id = id
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)

    def position(self):
        return (int(self.x), int(self.y))


class ParticleSimulation:
    def __init__(self, num_particles, width, height):
        self.num_particles = num_particles
        self.width = width
        self.height = height
        self.speed = 5
        self.rebound_force = 0.1
        self.particles = [
            Particle(i + 1, random.randint(0, width), random.randint(0, height), self.speed)
            for i in range(num_particles)
        ]

    def get_particle(self, particle_id):
        try:
            particle_id = int(particle_id)
        except Exception:
            particle_id = 0

        for particle in self.particles:
            if particle.id == particle_id:
                return particle

        return None

    def detect_collision(self, p1, p2):
        dx = p2.x - p1.x
        dy = p2.y - p1.y

        distance = math.sqrt(dx * dx + dy * dy)

        return distance < 2

    def resolve_collision(self, p1, p2):
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        angle = math.atan2(dy, dx)
        p1.vx -= self.rebound_force * math.cos(angle)
        p1.vy -= self.rebound_force * math.sin(angle)
        p2.vx += self.rebound_force * math.cos(angle)
        p2.vy += self.rebound_force * math.sin(angle)

    def update_particles(self):
        while True:
            for particle in self.particles:
                self._update(particle)
            for i in range(len(self.particles)):
                for j in range(i + 1, len(self.particles)):
                    if self.detect_collision(self.particles[i], self.particles[j]):
                        self.resolve_collision(self.particles[i], self.particles[j])

            time.sleep(0.1)

    def _update(self, particle):
        particle.x += particle.vx
        particle.y += particle.vy
        if particle.x <= 0 or particle.x >= self.width:
            particle.vx *= -1
        if particle.y <= 0 or particle.y >= self.height:
            particle.vy *= -1

    def save_png(self):
        plt.clf()
        x = [particle.x for particle in self.particles]
        y = [particle.y for particle in self.particles]
        plt.scatter(x, y)
        plt.xlim(0, self.width)
        plt.ylim(0, self.height)
        plt.title('Particle Simulation')
        plt.pause(0.01)

        now = datetime.now()

        date = now.strftime("%Y%m%d%H%M")

        filename = 'simulation_{}.png'.format(date)

        plt.savefig(filename)

        return filename


if __name__ == '__main__':
    factory = MyObjectFactory()

    cmd = IpServerCmd(factory)

    cmd.run()
