# -*- coding: gbk -*-

from TradeApi import *
from Utils import *
import xlrd

class StockPool(object):
    """��Ʊ��"""

    _tradeApi = None
    # structure of pooled stocks
    # { stock_code: ֤ȯ����
    #   stock_name: ֤ȯ����
    #   total_stock_shares: ֤ȯ����
    #   yesterday_closing_price: ���̼�
    #   harden_price: ��ͣ��
    #   stock_share_limit: ��ȯ����
    #   order_list: {order_id:share, order_id:share}
    # }
    _stock_pool = []
    
    def __init__(self, tradeApi):
        if not tradeApi.IsLogon():
            raise Exception("Need logon first")
        self._tradeApi = tradeApi
    
    def addStock(self, stock_code, stock_share_limit):
        """�ڹ�Ʊ�������ӵ�ֻ��Ʊ"""
        rst = api.Query("����֤ȯ")
        if not rst:
            return rst

        # ����֤ȯ��Ϣ
        stock_info = None
        for r in rst:
            if r[0] == stock_code:
                stock_info = r
                break

        if not stock_info:
            return u"û�ҵ���Ӧ��Ʊ"

        _stock_code = stock_info[0]
        _stock_name = stock_info[1]
        # ����֤ȯ����
        _stock_marginable_share = stock_info[2]

        rst = api.Query("����", zqdm=stock_code)
        if not rst:
            return rst
        _harden_price = round_up_decimal_2(float(rst[1][2])*1.1)

    def addStocks(self, stock_codes, stock_share_limits):
        """�ڹ�Ʊ��������һ���Ʊ"""
        pass
    
    def setShareLimit(self, stock_code, max_share):
        """���ù�Ʊ�ش洢��Ʊ���ֵ"""
        pass

    def getStockShare(self, stock_code):
        pass

    def getHardenPrice(self, stock_code):
        """�����ͣ��"""
        pass

    def getPooledStocks(self):
        """��ù�Ʊ���еĹ�Ʊ"""
        pass

    def fetch(self, stock_code=None):
        """�ӷ�������ȡ��Ʊ"""
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
    
    rst = api.Query("����֤ȯ")
    if not bool(rst):
        print bool(rst)
    
    for r in rst:
        if r[0] in stocks:
            i = stocks.index(r[0])
            print r[2]
            shares[i] = min(shares[i], int(int(r[2])/100)*100)

    print shares
    
    types = [3] * len(stocks)
    
    rst = api.Query("����", zqdm=stocks)
    if not rst:
        print("��ȡ����ʧ��")

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
