# -*- coding: utf-8 -*-

import sys

sys.path.append('../')

import logging
import gevent

from gevent.server import StreamServer
from datapacker import DataPacker
from factory import factory
from logging import handlers

from net import NetServer, ConnectionPool
from service import Service

factory.conn_pool = ConnectionPool()
factory.packer = DataPacker(1, 2)
factory.router = Service()

log = logging.getLogger('doo')
handle = logging.StreamHandler()
# handle = handlers.BaseRotatingHandler('./test.log', 'w+')
handle.setLevel(logging.INFO)
handle.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
log.addHandler(handle)


def test():
    s = StreamServer(('0.0.0.0', 8000), NetServer)
    s.start()
    gevent.wait()
    s.serve_forever()


if __name__ == '__main__':
    test()