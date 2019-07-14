# -*- coding: gbk -*-

from ctypes import *
from Utils import *
from ResultBuffer import *
from ErrorException import *
import datetime
import time

@Singleton
class MarketApi(Singleton):
    def __init__(self):
        self._ip = ""
        self._port = None
        self._isConnected = False
        # ʧ���׳�WindowsError�쳣
        self._dll = windll.LoadLibrary('TdxHqApi.dll')

    def Connect(self, ip, port):
        """ ���ӷ����� """
        assert(isValidIpAddress(ip))
        assert(type(port) is int)
        self._ip = ip
        self._port = port
        rst = ResultBuffer()
        ret_val = self._dll.TdxL2Hq_Connect(ip, port, rst.Result, rst.ErrInfo)
        if not ret_val:
            raise LogonError(ip, port, rst[0])
        self._isConnected = True

    def isConnected(self):
        return self._isConnected
    
    def Disconnect(self):
        if self._isConnected:
            self._dll.TdxL2Hq_Disconnect()

    def GetQuotes5(self, stocks):
        u""" ����嵵���� """
        assert type(stocks) in [list, str]
        assert self.isConnected()

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
            raise QueryError("�嵵����",rst[0])
        return rst[0]

    def GetQuotes10(self, stocks):
        u""" ���ʮ������ """
        assert self.isConnected()
        assert type(stocks) in [list, str]
        
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
            raise QueryError("ʮ������", rst[0])
        return rst[0]

    def GetMinuteTimeData(self, stock):
        u""" ��ȡ��ʱ���� """
        assert self.isConnected()
        assert(isValidStockCode(stock))

        market = c_byte(getMarketID(stock))
        rst = ResultBuffer()
        self._dll.TdxL2Hq_GetMinuteTimeData(market, stock, rst.Result, rst.ErrInfo)
        if not rst:
            raise QueryError("��ʱ����", rst[0])
        return rst[0]

    def GetTransactionData(self, stock, start, count):
        u""" ��ȡ��ȳɽ����� """
        assert self.isConnected()
        assert(isValidStockCode(stock))
        assert(type(start) is int and start >= 0)
        
        market = c_byte(getMarketID(stock))
        count_ref = byref(c_short(count))
        rst = ResultBuffer()
        self._dll.TdxL2Hq_GetTransactionData(market, stock, start, count_ref, rst.Result, rst.ErrInfo)
        if not rst:
            raise QueryError("��ȳɽ�", rst[0])
        return rst[0]

    def GetDetailTransactionData(self, stock, start, count):
        u""" ��ȡ��ȳɽ����� """
        assert self.isConnected()
        assert(isValidStockCode(stock))
        assert(type(start) is int and start >= 0)
        
        market = c_byte(getMarketID(stock))
        count_ref = byref(c_short(count))
        rst = ResultBuffer()
        self._dll.TdxL2Hq_GetDetailTransactionData(market, stock, start, count_ref, rst.Result, rst.ErrInfo)
        if not rst:
            raise QueryError("��ȳɽ�", rst[0])
        return rst[0]

    def GetSecurityCount(self, market):
        u""" ��ù�Ʊ���� ���ع�Ʊ���� """
        assert self.isConnected()
        res = ResultBuffer()
        count = c_short()
        count_ref = byref(count)
        self._dll.TdxL2Hq_GetSecurityCount(market, count_ref, res.ErrInfo)
        if not res:
            raise QueryError("��Ʊ����", rst[0], market=market)
        return count.value

    def GetSecurityList(self, market, start):
        u""" ���start��ʼ1000֧��Ʊ���� """
        assert self.isConnected()
        res = ResultBuffer()
        _strat = c_short(start)
        _count = c_short()
        _count_ref = byref(_count)
        self._dll.TdxL2Hq_GetSecurityList(market, start, _count_ref, res.Result, res.ErrInfo)
        if not res:
            raise QueryError("��Ʊ����", res[0])
        # TODO������������
        return res[0]
        
    def __del__(self):
        self.Disconnect()

def GetIndexBars(self):
    pass
    #TdxL2Hq_GetIndexBars()

if __name__ == "__main__":
    import os, msvcrt, signal
    def OnExit(signum, frame):
        print u"��������˳�"
        msvcrt.getch()
        lv2.Disconnect()
        exit()

    signal.signal(signal.SIGINT, OnExit)
    lv2 = MarketApi.Instance()
    lv2.Connect("119.97.185.4",7709)
    try:
        rst = lv2.GetTransactionData('600036',0,20)
        printd(rst.attr)
        for i in rst:
            printd([i])
        print len(rst)
    except ErrorException as e:
        print e
##    printd(rst.attr)
##    while(True):
##        os.system('cls')
##        out_str = u"==== "
##        out_str += time.strftime("%H:%M:%S")
##        out_str += "\n"
##        rst = lv2.GetQuotes10('601699')
##        rst = rst[0]
##        out_str += u"�ּ� " + rst["�ּ�"][:-4] + "\n"
##        out_str += u"--\n"
##
##        out_str += u"��ʮ " + rst["��ʮ��"][:-4] + " " + rst["��ʮ��"] + "\n"
##        out_str += u"���� " + rst["���ż�"][:-4] + " " + rst["������"] + "\n"
##        out_str += u"���� " + rst["���˼�"][:-4] + " " + rst["������"] + "\n"
##        out_str += u"���� " + rst["���߼�"][:-4] + " " + rst["������"] + "\n"
##        out_str += u"���� " + rst["������"][:-4] + " " + rst["������"] + "\n"
##        out_str += u"���� " + rst["�����"][:-4] + " " + rst["������"] + "\n"
##        out_str += u"���� " + rst["���ļ�"][:-4] + " " + rst["������"] + "\n"
##        out_str += u"���� " + rst["������"][:-4] + " " + rst["������"] + "\n"
##        out_str += u"���� " + rst["������"][:-4] + " " + rst["������"] + "\n"
##        out_str += u"��һ " + rst["��һ��"][:-4] + " " + rst["��һ��"] + "\n"
##        out_str += u"--\n"
##        out_str += u"��һ " + rst["��һ��"][:-4] + " " + rst["��һ��"] + "\n"
##        out_str += u"��� " + rst["�����"][:-4] + " " + rst["�����"] + "\n"
##        out_str += u"���� " + rst["������"][:-4] + " " + rst["������"] + "\n"
##        out_str += u"���� " + rst["���ļ�"][:-4] + " " + rst["������"] + "\n"
##        out_str += u"���� " + rst["�����"][:-4] + " " + rst["������"] + "\n"
##        out_str += u"���� " + rst["������"][:-4] + " " + rst["������"] + "\n"
##        out_str += u"���� " + rst["���߼�"][:-4] + " " + rst["������"] + "\n"
##        out_str += u"��� " + rst["��˼�"][:-4] + " " + rst["�����"] + "\n"
##        out_str += u"��� " + rst["��ż�"][:-4] + " " + rst["�����"] + "\n"
##        out_str += u"��ʮ " + rst["��ʮ��"][:-4] + " " + rst["��ʮ��"] + "\n"
##        
##        print out_str
##        time.sleep(0.5)

    lv2.Disconnect()
