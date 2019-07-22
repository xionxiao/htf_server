# -*- coding: gbk -*-

import redis,sys
sys.path.append("..")
from market import *

class RedisCache(object):
    def __init__(self, host='localhost', port=6379, db=0):
        self._db = redis.Redis(host, port, db)
        self._db.echo('hello')

    def CacheStock(self):
        lv2 = MarketApi.Instance()
        lv2.Connect("119.97.185.4",7709)
        start = 0
        market = 0
        while True:
            rst = lv2.GetSecurityList(market,start)
            for i in rst:
                self._db.set(i["代码"],i["名称"])
            if len(rst) != 1000:
                if market == 0:
                    market = 1
                    continue
                else:
                    break
            else:
                start += len(rst)
        self._db.save()
    
    def Get(self,key):
        return self._db.get(key)

    def Set(self, key, value):
        self._db.set(key, value)
            
            

if __name__ == "__main__":
    r = RedisCache()
    r.CacheStock()
