# -*- coding: gbk -*-

from TradeApi import *
import xlrd

class StckPool(object):
    """股票池"""

    trader = None
    
    def __init__(self):
        pass
    
    def addToStockPool(self, stock_code, max_share):
        """在股票池中增加监控的股票"""
        pass

    def setMaxShare(self, stock_code, max_share):
        """设置股票池存储股票最大值"""
        pass

    def getStockShare(self, stock_code):
        pass


if __name__ == "__main__":
    xls = xlrd.open_workbook('05a.xls')
    table = xls.sheets()[0]
    stocks = [i.encode() for i in table.col_values(0)]
    shares = [int(i) for i in table.col_values(1)]

    print stocks

    api = TradeApi()
    api.Open()
    rst = api.Logon("125.39.80.105", 443, "184039030", "326326")
    
    rst = api.Query("可融证券")
    if not bool(rst):
        print bool(rst)
    
    for r in rst:
        if r[0] in stocks:
            i = stocks.index(r[0])
            shares[i] = min(shares[i], int(r[2]))

    print shares
    
    types = [3] * len(stocks)
    
    rst = api.Query("行情", zqdm=stocks)
    if not rst:
        print("获取行情失败")

    prices = [ round(float(p[1][2])*1.1,2) for p in rst ]
    print prices

    rst = api.SendOrders(types, stocks, prices, shares)
    print rst
    
    api.Logoff()
    api.Close()
