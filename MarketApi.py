# -*- coding: gbk -*-

from ctypes import *
from Utils import *
from ResultBuffer import *
import datetime
import time

@Singleton
class MarketApi(Singleton):
    __ip = ""
    __port = None
    __isConnected = False

    def __init__(self):
        # ʧ���׳�WindowsError�쳣
        self._dll = windll.LoadLibrary('TdxHqApi.dll')

    def Connect(self, ip, port):
        """ ���ӷ����� """
        assert(isValidIpAddress(ip))
        assert(type(port) is int)
        self.__ip = ip
        self.__port = port
        rst = ResultBuffer()
        ret_val = self._dll.TdxL2Hq_Connect(ip, port, rst.Result, rst.ErrInfo)
        if not ret_val:
            # TODO: �滻ͨ���쳣
            raise Exception("Connect fail: " + rst.ErrInfo.value)
        self.__isConnected = True

    def Disconnect(self):
        if self.__isConnected:
            self._dll.TdxL2Hq_Disconnect()

    def GetQuotes5(self, stocks):
        u""" ����嵵���飬���ʧ�ܵ����쳣"""
        assert(type(stocks) in [list, str])
        assert(self.__isConnected)
        if type(stocks) is str:
            stocks = [stocks]
        count = len(stocks)
        markets = []
        for i in stocks:
            markets.append(getMarketID(i))
        c_stocks = c_array(stocks, c_char_p)
        c_markets = c_array(markets, c_byte)
        c_count = c_short()
        c_count.value = count
        c_count_ref = byref(c_count)
        rst = ResultBuffer()
        self._dll.TdxL2Hq_GetSecurityQuotes(c_markets, c_stocks, c_count_ref, rst.Result, rst.ErrInfo)
        if not rst:
            raise Exception, "��ȡ5������ʧ��:" + str(rst)
        return rst

    def GetQuotes10(self, stocks):
        assert(type(stocks) in [list, str])
        if type(stocks) is str:
            stocks = [stocks]
        count = len(stocks)
        markets = []
        for i in stocks:
            markets.append(getMarketID(i))
        c_stocks = c_array(stocks, c_char_p)
        c_markets = c_array(markets, c_byte)
        c_count = c_short(count)
        c_count_ref = byref(c_count)
        rst = ResultBuffer()
        self._dll.TdxL2Hq_GetSecurityQuotes10(c_markets, c_stocks, c_count_ref, rst.Result, rst.ErrInfo)
        if not rst:
            raise Exception, "��ȡ10������ʧ��:" + str(rst)
        return rst

    def GetMinuteTimeData(self, stock):
        u""" ��ȡ��ʱ���� """
        assert(isValidStockCode(stock))
        market = c_byte(getMarketID(stock))
        self._dll.TdxL2Hq_GetMinuteTimeData(market, stock, rst.Result, rst.ErrInfo)
        if not rst:
            raise Exception, "��ȡ��ʱ����ʧ��:" + str(rst)
        return rst
    
    def __del__(self):
        print "call __del__"
        self.Disconnect()

if __name__ == "__main__":
    lv2 = MarketApi.Instance()
    print lv2.Connect("61.135.142.90",443)
    for i in range(1):
        print "================= ",time.strftime("%H:%M:%S")
        rst = lv2.GetQuotes5('300001')
        print u"�ּ�", rst[0][0][3]
        print u"��һ",rst[0][0][17],rst[0][0][19]
        print u"��һ",rst[0][0][18],rst[0][0][20]
        #time.sleep(1)

    for i in range(2):
        printd(lv2.GetMinuteTimeData('601699')[0])
        time.sleep(1)
    lv2.Disconnect()
