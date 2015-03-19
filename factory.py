# -*- coding: utf-8 -*-

from utils.singleton import Singleton


class Factory(object):
    __metaclass__ = Singleton
    # conn_pool = ConnectionPool()
    # packer = DataPacker(1, 2)
    # router = Router()

    def __init__(self):
        self.conn_pool = None
        self.packer = None
        self.router = None


factory = Factory()