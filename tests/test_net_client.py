# -*- coding: utf-8 -*-

import sys

sys.path.append('../')

from gevent import socket
import gevent
from datapacker import DataPacker


CONNECTION_NUM = 10

packer = DataPacker(1, 2)


def connect_net_server(index):
    s = socket.socket()
    s.connect(('192.168.1.80', 8000))
    # print('index:%d' % index)
    # s.send('hello world\n')
    while True:
        if not s:
            print('sfsfsfsdf')
        gevent.sleep(2)


def test():
    jobs = []
    for i in xrange(CONNECTION_NUM):
        jobs.append(gevent.spawn(connect_net_server, i))
    gevent.joinall(jobs)


if __name__ == '__main__':
    test()