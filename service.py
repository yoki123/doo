# -*- coding: utf-8 -*-

from utils.log import log


class ConflictKey(Exception):
    pass


class Service(object):
    def __init__(self):
        self.map_target = {}

    def add_rules(self, key, target):
        if key in self.map_target:
            raise ConflictKey

        self.map_target[key] = target

    def route(self, key):
        def decorator(target):
            self.add_rules(key, target)
            return target

        return decorator

    def call(self, key, *args, **kw):
        target = self.map_target.get(key, )
        if not target:
            log.error('the key %d not found' % key)
            return None
        response = target(*args, **kw)
        return response
