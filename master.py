# -*- coding: utf-8 -*-

import multiprocessing
from worker import Worker
from netprotocol import j


class Master(object):
    '''Master process.'''

    def __init__(self):
        self._mq_map = []
        self._master_mq_read = None


    def config(self):
        pass


    def start(self):
        num_process = 3
        for i in xrange(num_process):
            mq = multiprocessing.Queue()
            self._mq_map.append(mq)

        plist = []
        for i in xrange(num_process):
            w = Worker(self._mq_map, i)
            p = multiprocessing.Process(target=w, args=())
            plist.append(p)
        for p in plist:
            p.start()

        for mq in self._mq_map:
            mq.put(j.dumps((1, 1, 'test', (2, 4))))

        for p in plist:
            p.join()
