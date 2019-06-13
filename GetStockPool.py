# -*- coding: gbk -*-

from TradeApi import *
from StockPool import *
from Utils import *
from Cache import *
import json

def getStockPool():
    api = TradeApi.Instance()
    if not api.isLogon():
        rst = api.Logon("125.39.80.105", 443, "184039030", "326326")
        if not rst:
            return u"���ӷ�����ʧ��"
    sp = StockPool.Instance()
    cache = Cache.Instance()
    sp.sync()
    stocks = sp.getStocks()
    for i in stocks.keys():
        stocks[i]["֤ȯ����"] = cache.get(i, "֤ȯ����")
        stocks[i]["��ͣ��"] = cache.get(i, "��ͣ��")
    json_dumps = json.dumps(stocks, encoding="gbk").decode("utf8")
    return json_dumps

if __name__ == "__main__":
    api = TradeApi.Instance()
    if not api.isLogon():
        rst = api.Logon("125.39.80.105", 443, "184039030", "326326")
    sp = StockPool.Instance()
    sp.addStock('600036', 1000)
    print "----"
    getStockPool()
