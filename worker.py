# -*- coding: utf-8 -*-

import sys
from netprotocol import j

if sys.platform != 'win32':
    import setproctitle


class Worker(object):
    def __init__(self, mq_map, p_name):
        self.mq_map = mq_map
        self.p_name = p_name
        self.mq_read = mq_map[p_name]
        self._proctitle = "doo: %s process" % self.p_name

    def config(self):
        pass

    def __call__(self):
        if sys.platform != 'win32':
            setproctitle.setproctitle(self._proctitle)

        self._run()

    def _run(self):
        while True:
            data = self.mq_read.get()
            req = j.loads(data)
            (msg_id, method, args) = self._parse_request(req)
            self._handle_request(method, args)

    def _parse_request(self, req):
        if (len(req) != 4 or req[0] != 1):
            raise Exception

        (_, msg_id, method_name, args) = req

        method = getattr(self, method_name)

        return (msg_id, method, args)

    def _handle_request(self, method, args):
        ret = method(*args)

    def test(self, x, y):
        print('hello: %d' % (x + y))

    def call(self, name, foo, arg):
        pass