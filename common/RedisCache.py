# -*- coding: gbk -*-

import redis,sys
sys.path.append("..")
from market import *
from utils import dumpUTF8Json

class RedisCache(object):
    def __init__(self, host='localhost', port=6379, db=0):
        self._db = redis.Redis(host, port, db)
        self._db.echo('hello')

    def CacheStock(self):
        lv2 = MarketApi.Instance()
        lv2.Connect("119.97.185.4",7709)
        obj = {}
        
        start = 0
        market = 0
        print lv2.GetSecurityCount(market)
        while True:
            rst = lv2.GetSecurityList(market,start)
            start += len(rst)
            for i in rst:
                key = i["代码"] + '.SZ'
                value = i["名称"]
                self._db.set(key,value)
                obj[key] = value
            if len(rst) < 1000:
                break
        print len(obj.keys())

        start = 0
        market = 1
        print lv2.GetSecurityCount(market)
        while True:
            rst = lv2.GetSecurityList(market,start)
            start += len(rst)
            for i in rst:
                key = i["代码"] + '.SH'
                value = i["名称"]
                self._db.set(key,value)
                obj[key] = value
            if len(rst) < 1000:
                break
        print len(obj.keys())
        json_str = dumpUTF8Json(obj)
        f = open("dump.json","w")
        f.write(json_str)
        f.close()
        self._db.save()
    
    def Get(self,key):
        return self._db.get(key)

    def Set(self, key, value):
        self._db.set(key, value)
            

if __name__ == "__main__":
    r = RedisCache()
    r.CacheStock()
