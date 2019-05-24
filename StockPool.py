# -*- coding: gbk -*-

from TradeApi import *
from Utils import *
import xlrd

class StockPool(object):
    """股票池"""

    _tradeApi = None
    # structure of pooled stocks
    # { stock_code: 证券代码
    #   stock_name: 证券名称
    #   total_stock_shares: 证券数量
    #   yesterday_closing_price: 收盘价
    #   harden_price: 涨停价
    #   stock_share_limit: 融券上限
    #   order_list: {order_id:share, order_id:share}
    # }
    _stock_pool = []
    
    def __init__(self, tradeApi):
        if not tradeApi.IsLogon():
            raise Exception("Need logon first")
        self._tradeApi = tradeApi
    
    def addStock(self, stock_code, stock_share_limit):
        """在股票池中增加单只股票"""
        rst = api.Query("可融证券")
        if not rst:
            return rst

        # 可融证券信息
        stock_info = None
        for r in rst:
            if r[0] == stock_code:
                stock_info = r
                break

        if not stock_info:
            return u"没找到相应股票"

        _stock_code = stock_info[0]
        _stock_name = stock_info[1]
        # 可融证券数量
        _stock_marginable_share = stock_info[2]

        rst = api.Query("行情", zqdm=stock_code)
        if not rst:
            return rst
        _harden_price = round_up_decimal_2(float(rst[1][2])*1.1)

    def addStocks(self, stock_codes, stock_share_limits):
        """在股票池中增加一组股票"""
        pass
    
    def setShareLimit(self, stock_code, max_share):
        """设置股票池存储股票最大值"""
        pass

    def getStockShare(self, stock_code):
        pass

    def getHardenPrice(self, stock_code):
        """获得涨停价"""
        pass

    def getPooledStocks(self):
        """获得股票池中的股票"""
        pass

    def fetch(self, stock_code=None):
        """从服务器获取股票"""
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
    #print grabStocks('05a.xls')
    api = TradeApi()
    api.Open()
    rst = api.Logon("119.147.80.108", 443, "184039030", "326326")
    sp = StockPool(api)
