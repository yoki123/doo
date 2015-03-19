# -*- coding: utf-8 -*-

import sys

sys.path.append('../')
import gevent

from utils.rpc import RPCClient

s = '!@#$%^&*()QWERRTYUIOSDFGHJKLXCVBNMTYFI&teyfiyebou23UNBO*UYG&YB&IYGO*UYtob23t2iu129880-fdvcbdshvbdjv232112hvbds' * 10

num = 20000


def client(method):
    c = RPCClient('127.0.0.1', 6000)
    print c.call(method)


jobs = [gevent.spawn(client, 'slowmethod'), gevent.spawn(client, 'fastmethod')]
gevent.joinall(jobs)