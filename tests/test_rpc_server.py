# -*- coding: utf-8 -*-

import sys

sys.path.append('../')
import gevent

from gevent.server import StreamServer
from gevent import spawn_later

from utils.rpc import RPCServer


qs = 0


def print_qps():
    global qs
    print('qps:%d' % qs)
    qs = 0
    spawn_later(1, print_qps)


# spawn_later(1, print_qps)


class MyServer(RPCServer):
    def foo(self, x, y, z):
        # print gevent.getcurrent()
        return x * y * z

    def data(self, d):
        return d

    def sum(self, x, y):
        global qs
        qs += 1
        return x, y

    def echo(self, buff):
        return buff

    def add(self, x, y):
        return x, y

    def slowmethod(self):

        for x in range(20000):  # This is, aprox, the time in ms (on my old I7)
            if x % 100 == 0:
                print ("x: {}".format(x))
            for n in range(10000):
                y = x * x
            gevent.sleep(0)

        return 'Slow Done'

    def fastmethod(self):
        return 'Fast Done'


s = StreamServer(('127.0.0.1', 6000), MyServer())
s.serve_forever()