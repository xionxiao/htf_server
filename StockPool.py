# -*- coding: gbk -*-

from TradeApi import *
import xlrd

class StckPool(object):
    """股票池"""

    _tradeAPI = None
    # structure of pooled stocks
    # { stock_code: 
    #   stock_name:
    #   total_stock_shares:
    #   harden_price:
    # }
    _stock_pool = []


    
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


def grabStocks(xls_file):
    xls = xlrd.open_workbook(xls_file)
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
            print r[2]
            shares[i] = min(shares[i], int(int(r[2])/100)*100)

    print shares
    
    types = [3] * len(stocks)
    
    rst = api.Query("行情", zqdm=stocks)
    if not rst:
        print("获取行情失败")

    prices = [ round_up_decimal_2(float(p[1][2])*1.1) for p in rst ]
    print prices
    
    rst = api.SendOrders(types, stocks, prices, shares)
    print rst
    
    api.Logoff()
    api.Close()

if __name__ == "__main__":
    print grabStocks('05a.xls')
