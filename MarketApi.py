# -*- coding: gbk -*-

from ctypes import *
from Utils import *
from ResultBuffer import *
import datetime
import time

@Singleton
class MarketApi(Singleton):
    def __init__(self):
        self._ip = ""
        self._port = None
        self._isConnected = False
        # 失败抛出WindowsError异常
        self._dll = windll.LoadLibrary('TdxHqApi.dll')

    def Connect(self, ip, port):
        """ 连接服务器 """
        assert(isValidIpAddress(ip))
        assert(type(port) is int)
        self._ip = ip
        self._port = port
        rst = ResultBuffer()
        ret_val = self._dll.TdxL2Hq_Connect(ip, port, rst.Result, rst.ErrInfo)
        if not ret_val:
            # TODO: 替换通用异常
            raise Exception("Connect fail: " + rst.ErrInfo.value)
        self._isConnected = True

    def isConnected(self):
        return self._isConnected
    
    def Disconnect(self):
        if self._isConnected:
            self._dll.TdxL2Hq_Disconnect()

    def GetQuotes5(self, stocks):
        u""" 获得五档行情 """
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
            raise Exception, "获取5档行情失败:" + str(rst)
        return rst[0]

    def GetQuotes10(self, stocks):
        u""" 获得十档报价 """
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
            # TODO: customer exception
            raise Exception, "获取10档行情失败:" + str(rst)
        return rst[0]

    def GetMinuteTimeData(self, stock):
        u""" 获取分时数据 """
        assert self.isConnected()
        assert(isValidStockCode(stock))

        market = c_byte(getMarketID(stock))
        rst = ResultBuffer()
        self._dll.TdxL2Hq_GetMinuteTimeData(market, stock, rst.Result, rst.ErrInfo)
        if not rst:
            raise Exception, "获取分时数据失败:" + str(rst)
        return rst[0]

    def GetDetailTransactionDate(self, stock, start, count):
        u""" 获取逐比成交数据 """
        assert self.isConnected()
        assert(isValidStockCode(stock))
        assert(type(start) is int and start >= 0)
        
        market = c_byte(getMarketID(stock))
        count_ref = byref(c_short(count))
        rst = ResultBuffer()
        self._dll.TdxL2Hq_GetDetailTransactionData(market, stock, start, count_ref, rst.Result, rst.ErrInfo)
        if not rst:
            raise Exception, "获取逐比数据失败:" + str(rst)
        return rst
    
    def __del__(self):
        self.Disconnect()

if __name__ == "__main__":
    import os, msvcrt, signal
    def OnExit(signum, frame):
        print u"按任意键退出"
        msvcrt.getch()
        lv2.Disconnect()
        exit()

    signal.signal(signal.SIGINT, OnExit)
    lv2 = MarketApi.Instance()
    lv2.Connect("119.97.185.4",7709)
##    rst = lv2.GetDetailTransactionDate('600104',0,10)
##    for i in range(10):
##        printd(rst[0][i])
##    printd(rst[0].attr())
    while(True):
        os.system('cls')
        out_str = u"==== "
        out_str += time.strftime("%H:%M:%S")
        out_str += "\n"
        rst = lv2.GetQuotes10('601699')
        rst = rst[0]
        out_str += u"现价 " + rst["现价"][:-4] + "\n"
        out_str += u"--\n"

        out_str += u"卖十 " + rst["卖十价"][:-4] + " " + rst["卖十量"] + "\n"
        out_str += u"卖九 " + rst["卖九价"][:-4] + " " + rst["卖九量"] + "\n"
        out_str += u"卖八 " + rst["卖八价"][:-4] + " " + rst["卖八量"] + "\n"
        out_str += u"卖七 " + rst["卖七价"][:-4] + " " + rst["卖七量"] + "\n"
        out_str += u"卖六 " + rst["卖六价"][:-4] + " " + rst["卖六量"] + "\n"
        out_str += u"卖五 " + rst["卖五价"][:-4] + " " + rst["卖五量"] + "\n"
        out_str += u"卖四 " + rst["卖四价"][:-4] + " " + rst["卖四量"] + "\n"
        out_str += u"卖三 " + rst["卖三价"][:-4] + " " + rst["卖三量"] + "\n"
        out_str += u"卖二 " + rst["卖二价"][:-4] + " " + rst["卖二量"] + "\n"
        out_str += u"卖一 " + rst["卖一价"][:-4] + " " + rst["卖一量"] + "\n"
        out_str += u"--\n"
        out_str += u"买一 " + rst["买一价"][:-4] + " " + rst["买一量"] + "\n"
        out_str += u"买二 " + rst["买二价"][:-4] + " " + rst["买二量"] + "\n"
        out_str += u"买三 " + rst["买三价"][:-4] + " " + rst["买三量"] + "\n"
        out_str += u"买四 " + rst["买四价"][:-4] + " " + rst["买四量"] + "\n"
        out_str += u"买五 " + rst["买五价"][:-4] + " " + rst["买五量"] + "\n"
        out_str += u"买六 " + rst["买六价"][:-4] + " " + rst["买六量"] + "\n"
        out_str += u"买七 " + rst["买七价"][:-4] + " " + rst["买七量"] + "\n"
        out_str += u"买八 " + rst["买八价"][:-4] + " " + rst["买八量"] + "\n"
        out_str += u"买九 " + rst["买九价"][:-4] + " " + rst["买九量"] + "\n"
        out_str += u"买十 " + rst["买十价"][:-4] + " " + rst["买十量"] + "\n"
        
        print out_str
        time.sleep(0.5)

    lv2.Disconnect()
