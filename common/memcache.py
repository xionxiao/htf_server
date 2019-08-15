# -*- coding: gbk -*-

from couchbase.bucket import Bucket
from couchbase.exceptions import CouchbaseError

def _toUTF8(ss):
    return ss.decode('gbk').encode('utf8')

class Cache(object):
    """ 缓存系统 """

    def __init__(self, host='localhost', port=12000, debug=0):
        try:
            self._db = Bucket('couchbase://192.168.1.112/Cache')
        except:
            self._db = None

    def get(self, key):
        if self._db:
            try:
                v = self._db.get(_toUTF8(key))
                value = v.value.encode('gbk')
                return value
            except CouchbaseError:
                return None
        return None

    def set(self, key, value, expire_seconds=0):
        if self._db:
            key = _toUTF8(key)
            value = _toUTF8(value)
            if expire_seconds:
                return self._db.setex(key, value, expire_seconds)
            else:
                return self._db.set(key, value)
        return None


if __name__ == "__main__":
    c = Cache('192.168.1.112',8091)
    c.set('你好','世界')
    print c.get('你好')
    print c.get('000625')
    
