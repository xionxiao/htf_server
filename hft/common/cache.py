# -*- coding: utf8 -*-

import redis


class Cache(object):

    u""" 缓存系统 """

    def __init__(self, host='localhost', port=6379, db=0):
        try:
            self._db = redis.Redis(host, port, db)
            self._db.echo('hello')
        except:
            self._db = None

    def get(self, key):
        if self._db:
            return self._db.get(key)
        return None

    def set(self, key, value, expire_seconds=0):
        if self._db:
            if expire_seconds:
                return self._db.setex(key, value, expire_seconds)
            else:
                return self._db.set(key, value)
        return None

