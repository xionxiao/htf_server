# -*- coding: gbk -*-

from TradeApi import *
import xlrd

class StckPool(object):
    def addToStockPool(self, stock_code, max_share):
        """在股票池中增加股票"""
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
    types = [int(i) for i in table.col_values(1)]
    prices = [float(i) for i in table.col_values(2)]
    shares = [int(i) for i in table.col_values(3)]

    print stocks

    api = TradeApi()
    api.Open()
    rst = api.Logon("125.39.80.105", 443, "184039030", "326326")
    print "connect " + str(bool(rst))
    rst = api.Query("可融证券")
    if not bool(rst):
        print bool(rst)
    
    ss = str(rst['result'])
    # print str(rst)
    rows = ss.split('\n')
    print len(rows)
    tabs = [ i.split('\t') for i in rows ]
    
    for r in tabs:
        if r[0] in stocks:
            x = stocks.index(r[0])
            shares[x] = min(shares[x], int(r[2]))

    print shares

    print prices
    rst = api.SendOrders(types, stocks, prices, shares)
    #rst = api.SendOrder(3, "601998", 8.38, 100)
    print rst
    api.Logoff()
    api.Close()
