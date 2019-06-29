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
    import os, msvcrt, signal
    def OnExit(signum, frame):
        print u"��������˳�"
        msvcrt.getch()
        lv2.Disconnect()
        exit()

    signal.signal(signal.SIGINT, OnExit)
    lv2 = MarketApi.Instance()
    print lv2.Connect("61.135.142.90",443)
    while(True):
        os.system('cls')
        out_str = u"==== "
        out_str += time.strftime("%H:%M:%S")
        out_str += "\n"
        rst = lv2.GetQuotes10('601699')
        out_str += u"�ּ� " + rst[0][0][3][:-4] + "\n"
        out_str += u"--\n"

        out_str += u"��ʮ " + rst[0][0][59][:-4] + " " + rst[0][0][61] + "\n"
        out_str += u"���� " + rst[0][0][55][:-4] + " " + rst[0][0][57] + "\n"
        out_str += u"���� " + rst[0][0][51][:-4] + " " + rst[0][0][53] + "\n"
        out_str += u"���� " + rst[0][0][47][:-4] + " " + rst[0][0][49] + "\n"
        out_str += u"���� " + rst[0][0][43][:-4] + " " + rst[0][0][45] + "\n"
        out_str += u"���� " + rst[0][0][34][:-4] + " " + rst[0][0][36] + "\n"
        out_str += u"���� " + rst[0][0][30][:-4] + " " + rst[0][0][32] + "\n"
        out_str += u"���� " + rst[0][0][26][:-4] + " " + rst[0][0][28] + "\n"
        out_str += u"���� " + rst[0][0][22][:-4] + " " + rst[0][0][24] + "\n"
        out_str += u"��һ " + rst[0][0][18][:-4] + " " + rst[0][0][20] + "\n"
        out_str += u"--\n"
        out_str += u"��һ " + rst[0][0][17][:-4] + " " + rst[0][0][19] + "\n"
        out_str += u"��� " + rst[0][0][21][:-4] + " " + rst[0][0][23] + "\n"
        out_str += u"���� " + rst[0][0][25][:-4] + " " + rst[0][0][27] + "\n"
        out_str += u"���� " + rst[0][0][29][:-4] + " " + rst[0][0][31] + "\n"
        out_str += u"���� " + rst[0][0][33][:-4] + " " + rst[0][0][35] + "\n"
        out_str += u"���� " + rst[0][0][42][:-4] + " " + rst[0][0][44] + "\n"
        out_str += u"���� " + rst[0][0][46][:-4] + " " + rst[0][0][48] + "\n"
        out_str += u"��� " + rst[0][0][50][:-4] + " " + rst[0][0][52] + "\n"
        out_str += u"��� " + rst[0][0][54][:-4] + " " + rst[0][0][56] + "\n"
        out_str += u"��ʮ " + rst[0][0][58][:-4] + " " + rst[0][0][60] + "\n"
        
        print out_str
        time.sleep(0.5)

    lv2.Disconnect()
