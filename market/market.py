# -*- coding: utf8 -*-

from ctypes import *
import os

try:
    from common.error import *
    from common.utils import *
    from common.utils import c_array
    from common.resultbuffer import *
except ImportError:
    import sys
    sys.path.append("..")
    from common.error import *
    from common.utils import *
    from common.utils import c_array
    from common.resultbuffer import *


@Singleton
class MarketApi(Singleton):

    def __init__(self):
        self._ip = ""
        self._port = None
        self._isConnected = False
        # 失败抛出WindowsError异常
        path = os.path.split(os.path.realpath(__file__))[0]
        self._dll = windll.LoadLibrary(path + '\\market.dll')

    def Connect(self, ip, port):
        u""" 连接服务器 """
        assert(isValidIpAddress(ip))
        assert(type(port) is int)
        self._ip = ip
        self._port = port
        rst = ResultBuffer()
        ret_val = self._dll.TdxL2Hq_Connect(ip, port, rst.Result, rst.ErrInfo)
        if not ret_val:
            raise LogonError(ip, port, rst[0])
        self._isConnected = True

    def ReConnect(self):
        u""" 重新连接服务器 """
        self.Connect(self._ip, self._port)

    def isConnected(self):
        return self._isConnected

    def Disconnect(self):
        if self._isConnected:
            self._dll.TdxL2Hq_Disconnect()
            self._isConnected = False

    def GetQuotes5(self, stocks):
        u""" 获得五档行情 """
        assert type(stocks) in [list, str, StockCode]
        assert self.isConnected()

        if type(stocks) is not list:
            stocks = [stocks]
        count = len(stocks)
        for i in range(count):
            if type(stocks[i]) is not StockCode:
                stocks[i] = StockCode(stocks[i])

        c_stocks = c_array(map(lambda x: x.stock_code, stocks), c_char_p)
        c_markets = c_array(map(lambda x: x.market_id, stocks), c_byte)
        c_count = c_short()
        c_count.value = count
        c_count_ref = byref(c_count)
        rst = ResultBuffer()
        self._dll.TdxL2Hq_GetSecurityQuotes(
            c_markets, c_stocks, c_count_ref, rst.Result, rst.ErrInfo)
        if not rst:
            raise QueryError("五档行情", rst[0])
        return rst[0]

    def GetQuotes10(self, stocks):
        u""" 获得十档报价 """
        assert type(stocks) in [list, str, StockCode]
        assert self.isConnected()

        if type(stocks) is not list:
            stocks = [stocks]
        count = len(stocks)
        for i in range(count):
            if type(stocks[i]) is not StockCode:
                stocks[i] = StockCode(stocks[i])

        c_stocks = c_array(map(lambda x: x.stock_code, stocks), c_char_p)
        c_markets = c_array(map(lambda x: x.market_id, stocks), c_byte)
        c_count = c_short()
        c_count.value = count
        c_count_ref = byref(c_count)
        rst = ResultBuffer()
        self._dll.TdxL2Hq_GetSecurityQuotes10(
            c_markets, c_stocks, c_count_ref, rst.Result, rst.ErrInfo)
        if not rst:
            raise QueryError("十档行情", rst[0])
        return rst[0]

    def GetMinuteTimeData(self, stock):
        u""" 获取分时数据 """
        assert self.isConnected()
        assert(type(stock) in (StockCode, str))

        stock = StockCode(stock)
        market = c_byte(stock.market_id)
        rst = ResultBuffer()
        self._dll.TdxL2Hq_GetMinuteTimeData(
            market, stock.stock_code, rst.Result, rst.ErrInfo)
        if not rst:
            raise QueryError("分时数据", rst[0])
        return rst[0]

    # def GetHistoryMinuteTime(self):
    #     pass

    def GetTransactionData(self, stock, count=2000, start=0):
        u""" 获取逐比成交数据 count 最大2000"""
        assert self.isConnected()
        assert(type(stock) in (StockCode, str))
        assert(type(start) is int and start >= 0)

        stock = StockCode(stock)
        market = c_byte(stock.market_id)
        count_ref = byref(c_short(count))
        rst = ResultBuffer()
        self._dll.TdxL2Hq_GetTransactionData(
            market, stock.stock_code, start, count_ref,
            rst.Result, rst.ErrInfo)
        if not rst:
            raise QueryError("逐比成交", rst[0])
        return rst[0]

    # def GetHistoryTransactionData(self):
    #     pass

    def GetDetailTransactionData(self, stock, count=2000, start=0):
        u""" 获取逐比成交数据 count 最大2000"""
        assert self.isConnected()
        assert(type(stock) in (StockCode, str))
        assert(type(start) is int and start >= 0)

        stock = StockCode(stock)
        market = c_byte(stock.market_id)
        count_ref = byref(c_short(count))
        rst = ResultBuffer()
        self._dll.TdxL2Hq_GetDetailTransactionData(
            market, stock.stock_code, start, count_ref,
            rst.Result, rst.ErrInfo)
        if not rst:
            raise QueryError("逐比成交", rst[0])
        return rst[0]

    def GetSecurityCount(self, market):
        u""" 获得股票数量 返回股票数量 """
        assert self.isConnected()

        res = ResultBuffer()
        count = c_short()
        count_ref = byref(count)
        self._dll.TdxL2Hq_GetSecurityCount(market, count_ref, res.ErrInfo)
        if not res:
            raise QueryError("股票数量", rst[0], market=market)
        return count.value

    def GetSecurityList(self, market, start):
        u""" 获得start开始1000支股票代码 """
        assert self.isConnected()
        res = ResultBuffer()
        _start = c_short(start)
        _count = c_short()
        _count_ref = byref(_count)
        self._dll.TdxL2Hq_GetSecurityList(
            market, _start, _count_ref, res.Result, res.ErrInfo)
        if not res:
            raise QueryError("股票代码", res[0])
        # TODO：处理返回数量
        return res[0]

    def __del__(self):
        self.Disconnect()

    def GetIndexBars(self, stock, period='1d', start=0, count=800):
        u""" 获取K线数据
            period：K线周期 [1m,5m,15m,30m,1h,1d,1w,1M,1Q,1Y]
                    或者0-11数字：
                                    0->5分钟K线
                                    1->15分钟K线
                                    2->30分钟K线
                                    3->1小时K线
                                    4->日K线
                                    5->周K线
                                    6->月K线
                                    7->1分钟
                                    8->1分钟K线
                                    9->日K线
                                    10->季K线
                                    11->年K线
            start: K线开始位置,最后一条K线位置是0, 前一条是1, 依此类推
            count: 请求K线的数目, 最大值为800
        """
        pass
        # self._dll.TdxL2Hq_GetIndexBars()
        # TdxL2Hq_GetIndexBars()

    #  def GetSecurityBars():
    #    pass

    # def GetBuySellQueue(self, stock):
    #     pass

    # def GetCompanyInfoCategory(self):
    #     pass

    # def GetCompanyInfo(self):
    #     pass

    # def GetXDXRInfo(self):
    #     pass

    # def GetFinanceInfo(self):
    #     pass

if __name__ == "__main__":
    import msvcrt
    import signal

    def OnExit(signum, frame):
        print u"按任意键退出"
        msvcrt.getch()
        lv2.Disconnect()
        exit()

    signal.signal(signal.SIGINT, OnExit)
    lv2 = MarketApi.Instance()
    lv2.Connect("119.97.185.4", 7709)

    try:
        rst = lv2.GetQuotes10(['600036.SH', "sh000001"])
        for i in rst:
            print("------")
            for k, v in i.iteritems():
                print k.decode('utf8'), v.decode('utf8')

        rst = lv2.GetTransactionData("000001.SH", 10)
        print unicode(str(rst), 'utf8')

        lv2.Disconnect()
    except ErrorException as e:
        print e
