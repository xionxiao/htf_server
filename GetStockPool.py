# -*- coding: gbk -*-

from TradeApi import *
from StockPool import *
from Utils import *
from Cache import *
import json

def getStockPool():
    api = TradeApi()
    if not api.isLogon():
        rst = api.Logon("125.39.80.105", 443, "184039030", "326326")
        if not rst:
            return u"���ӷ�����ʧ��"
    sp = StockPool(api)
    cache = Cache(api)
    sp.sync()
    stocks = sp.getStocks()
    for i in stocks.keys():
        stocks[i]["֤ȯ����"] = cache.get(i, "֤ȯ����")
        stocks[i]["��ͣ��"] = cache.get(i, "��ͣ��")
    json_dumps = json.dumps(stocks, encoding="gbk").decode("utf8")
    return json_dumps

if __name__ == "__main__":
    api = TradeApi()
    if not api.isLogon():
        rst = api.Logon("125.39.80.105", 443, "184039030", "326326")
    sp = StockPool(api)
    sp.addStock('600036', 1000)
    print "----"
    getStockPool()
