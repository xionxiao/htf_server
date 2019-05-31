# -*- coding: gbk -*-

from TradeApi import *
from StockPool import *
from Utils import *
import json

def getStockPool():
    api = TradeApi()
    if not api.isLogon():
        api.Open()
        rst = api.Logon("125.39.80.105", 443, "184039030", "326326")
        if not rst:
            return ""
    sp = StockPool(api)
    sp.sync()
    stocks = sp.getStocks()
    json_dumps = json.dumps(stocks, encoding="gbk").decode("utf8")
    return json_dumps

if __name__ == "__main__":
    api = TradeApi()
    if not api.isLogon():
        api.Open()
        rst = api.Logon("125.39.80.105", 443, "184039030", "326326")
        if not rst:
            print rst
    sp = StockPool(api)
    sp.addStock('600036', 1000)
    print "----"
    getStockPool()
