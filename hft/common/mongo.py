# -*- coding: utf8 -*-

from pymongo import MongoClient
from pymongo.errors import *
from _stockcode_hashmap import StockCodeHashmap
from utils import StockCode
import threadpool
import os
from threading import Lock
from datetime import datetime
try:
    from market import *
except Exception, e:
    import sys
    sys.path.append("..")
    from market import *
    from common.error import QueryError

lock = Lock()
#data = []
def get_data(i):
    rst = lv2.GetCandleStickData('SH000001', '1d', i)
    if len(rst) == 1:
        #lock.acquire()
        data.append(rst[0])
        #lock.release()

def timeCost(request, n):
  print "Elapsed time: %s" % n
  
if __name__ == "__main__":
    
    lv2 = MarketApi.Instance()
    lv2.Connect("61.152.107.173", 7707)

##    pool = threadpool.ThreadPool(50)
##    reqs = threadpool.makeRequests(get_data, range(2200))
##    st = datetime.now()
##    print st
##    [ pool.putRequest(req) for req in reqs ]
##    pool.wait()
##    et = datetime.now()
##    print 'time',et-st
##    os.system('pause')
##    exit()
    
    client = MongoClient(host="192.168.1.108", port=27017)
    db = client.get_database('1d')
    
    try:
        cs = db.collection_names()
        for k in StockCodeHashmap.keys():
            stock = StockCode(k).format(suffix=False, prefix=True)
            if (stock in cs):
                continue
            try:
                collection = db.create_collection(stock)
                cs = db.collection_names()
                print "create", stock
            except CollectionInvalid:
                print stock, 'Exist'
                continue
            try:
                data = []
                for i in range(2200):
                    rst = lv2.GetCandleStickData(stock, '1d', i)
                    if len(rst) == 1:
                        data.append(rst[0])
                    else:
                        break
            except QueryError as e:
                print unicode(e.feedback.raw, 'utf8')
                #collection.drop()
                #print 'drop',stock
                lv2.ReConnect()
                continue
            print stock, 'insert', len(data)
            try:
                if len(data) > 0:
                    collection.insert_many(data)
            except TypeError as e:
                print type(e),e
                continue

        client.close()
        lv2.Disconnect()
    except Exception as e:
        print type(e),e
    finally:
        os.system('pause')
