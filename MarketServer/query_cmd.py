# -*- coding: gbk -*-

import sys,os,json
sys.path.append("..")
from command import *
from common.error import *
from common.utils import dumpUTF8Json
from market import MarketApi

def _check_and_reconnect(feedback):
    if feedback.raw == "发送数据失败, 请重新连接服务器":
        lv2 = MarketApi.Instance()
        lv2.Connect("119.97.185.4",7709)

class QueryMinuteTimeDataCmd(Command):
    def __init__(self, stock, handler):
        Command.__init__(self, handler)
        self._stock = stock
        self._handler = handler

    def execute(self):
        try:
            lv2 = MarketApi.Instance()
            rst = lv2.GetMinuteTimeData(self._stock)
            obj = {"minute":[]}
            for i in rst:
                obj["minute"].append(i)
            json_str = dumpUTF8Json(obj)
            self._handler.write(json_str)
        except QuerryError as e:
            err_str = dumpUTF8Json({"error":str(e)})
            self._handler.write(err_str)
            _check_and_reconnect(e.feedback)
        finally:
            self.complete()

class QueryQuote10Cmd(Command):
    def __init__(self, stocks, handler):
        Command.__init__(self, handler)
        self._stocks = stocks
        self._handler = handler

    def execute(self):
        try:
            lv2 = MarketApi.Instance()
            rst = lv2.GetQuotes10(self._stocks)
            obj = {"quote10":[]}
            # r = RedisCache()
            for i in rst:
                obj["quote10"].append(i)
            json_str = dumpUTF8Json(obj)
            self._handler.write(json_str)
        except QueryError as e:
            err_str = dumpUTF8Json({"error":str(e)})
            self._handler.write(err_str)
            _check_and_reconnect(e.feedback)
        finally:
            self.complete()
        

class QueryQuote5Cmd(Command):
    def __init__(self, stocks, handler):
        Command.__init__(self, handler)
        self._stocks = stocks
        self._handler = handler

    def execute(self):
        try:
            lv2 = MarketApi.Instance()
            rst = lv2.GetQuotes5(self._stocks)
            json_obj = {"quote5":[]}
            # r = RedisCache()
            for i in rst:
                json_obj["quote5"].append(i)
            json_str = dumpUTF8Json(json_obj)
            self._handler.write(json_str)
        except QueryError as e:
            err_str = dumpUTF8Json({"error":str(e)})
            self._handler.write(err_str)
        finally:
            self.complete()

class QueryTransactionCmd(Command):
    def __init__(self, stock, handler):
        Command.__init__(self, handler)
        self._stock = stock
        self._handler = handler

    def execute(self):
        try:
            lv2 = MarketApi.Instance()
            rst = lv2.GetTransactionData(self._stock, 0, 20)
            data = {"transaction": [i for i in rst]}
            ret_val = dumpUTF8Json(data)
            self._handler.write(ret_val)
        except QueryError as e:
            ret_val = dumpUTF8Json({"error":str(e)})
            self._handler.write(ret_val)
        finally:
            self.complete()


class QueryTransactionDetailCmd(Command):
    def __init__(self, stock, handler):
        Command.__init__(self, handler)
        self._stock = stock
        self._handler = handler

    def execute(self):
        try:
            lv2 = MarketApi.Instance()
            rst = lv2.GetDetailTransactionData(self._stock, 0, 20)
            data = {"transaction_detail": [i for i in rst]}
            ret_val = dumpUTF8Json(data)
            self._handler.write(ret_val)
        except QueryError as e:
            ret_val = dumpUTF8Json({"error":str(e)})
            self._handler.write(ret_val)
        finally:
            self.complete()
