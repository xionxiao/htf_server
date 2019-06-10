# -*- coding: gbk -*-

from ctypes import *
from Utils import *
from ResultBuffer import *
import datetime
import time

class Lv2Api(Singleton):
    __ip = ""
    __port = None

    def __init__(self):
        self._dll = windll.LoadLibrary('TdxHqApi.dll')
        lv2.Connect("61.135.142.90", 443)

    def Connect(self, ip, port):
        self.__ip = ip
        self.__port = port
        rst = ResultBuffer()
        self._dll.TdxL2Hq_Connect(ip, port, rst.Result, rst.ErrInfo)
        return rst

    def Disconnect(self):
        self._dll.TdxL2Hq_Disconnect()

    def GetQuotes10(self, stocks):
        assert(type(stocks) in [list, str])
        if type(stocks) is str:
            assert isValidStockCode(stocks)
            stocks = [stocks]
        count = len(stocks)
        markets = []
        for i in stocks:
            assert isValidStockCode(i)
            if i[0] == '6':
                markets.append(1)
            else:
                markets.append(0)
        c_stocks = c_array(stocks, c_char_p)
        c_markets = c_array(markets, c_byte)
        c_count = c_short(count)
        c_count_ref = byref(c_count)
        rst = ResultBuffer()
        self._dll.TdxL2Hq_GetSecurityQuotes10(c_markets, c_stocks, c_count_ref, rst.Result, rst.ErrInfo)
        return rst

    def GetQuotes5(self, stocks):
        assert(type(stocks) in [list, str])
        if type(stocks) is str:
            stocks = [stocks]
        count = len(stocks)
        markets = []
        for i in stocks:
            if i[0] == '6':
                markets.append(1)
            else:
                markets.append(0)
        c_stocks = c_array(stocks, c_char_p)
        c_markets = c_array(markets, c_byte)
        c_count = c_short()
        c_count.value = count
        c_count_ref = byref(c_count)
        rst = ResultBuffer()
        self._dll.TdxL2Hq_GetSecurityQuotes(c_markets, c_stocks, c_count_ref, rst.Result, rst.ErrInfo)
        return rst

    def GetMinuteTimeData(self, stock):
        assert(type(stock is str))
        if stock[0] == '6':
            market = c_byte(1)
        else:
            market = c_byte(0)
        rst = ResultBuffer()
        self._dll.TdxL2Hq_GetMinuteTimeData(market, stock, rst.Result, rst.ErrInfo)
        return rst
    
    def __del__(self):
        self.Disconnect()

if __name__ == "__main__":
    lv2 = Lv2Api()
    printd(lv2.Connect("61.135.142.90", 443))
    for i in range(30):
        print "================= ",time.strftime("%H:%M:%S")
        rst = lv2.GetQuotes10(['300001'])
        print u"现价", rst[0][0][3]
        print u"买一",rst[0][0][17],rst[0][0][19]
        print u"卖一",rst[0][0][18],rst[0][0][20]
        #time.sleep(1)
    lv2.Disconnect()
