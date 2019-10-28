# -*- coding: utf8 -*-

try:
    import sys
    sys.path.append("..")
    from common.command import *
    from common.error import *
    from common.utils import dumpUTF8Json, StockCode
    from market import MarketApi
except ImportError:
    import sys
    sys.path.append("..")
    from common.command import *
    from common.error import *
    from common.utils import dumpUTF8Json, StockCode
    from market import MarketApi


def _check_and_reconnect(feedback):
    # TODO:
    # Check in ThreadInvoker
    if feedback.raw == "发送数据失败, 请重新连接服务器":
        lv2 = MarketApi.Instance()
        lv2.Connect("119.97.185.4", 7709)


class QueryMinuteTimeDataCmd(Command):

    def __init__(self, stock, handler):
        Command.__init__(self, handler)
        self._stock = stock
        self._handler = handler

    def execute(self):
        try:
            lv2 = MarketApi.Instance()
            rst = lv2.GetMinuteTimeData(self._stock)
            obj = {"minute": []}
            for i in rst:
                obj["minute"].append(i)
            json_str = dumpUTF8Json(obj)
            self._handler.write(json_str)
        except QueryError as e:
            err_str = dumpUTF8Json({"error": str(e)})
            self._handler.write(err_str)
            _check_and_reconnect(e.feedback)
            self.complete()
        else:
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
            obj = {"quote10": []}
            for i in rst:
                i["名称"] = StockCode(i["代码"], i["市场"]).getStockName()
                obj["quote10"].append(i)
            json_str = dumpUTF8Json(obj)
            self._handler.write(json_str)
        except QueryError as e:
            err_str = dumpUTF8Json({"error": str(e)})
            self._handler.write(err_str)
            _check_and_reconnect(e.feedback)
            self.complete()
        else:
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
            json_obj = {"quote5": []}
            for i in rst:
                i["名称"] = StockCode(i["代码"], i["市场"]).getStockName()
                json_obj["quote5"].append(i)
            json_str = dumpUTF8Json(json_obj)
            self._handler.write(json_str)
        except QueryError as e:
            err_str = dumpUTF8Json({"error": str(e)})
            self._handler.write(err_str)
            self.complete()
        else:
            self.complete()


class QueryTransactionCmd(Command):

    def __init__(self, stock, handler):
        Command.__init__(self, handler)
        self._stock = stock
        self._handler = handler

    def execute(self):
        try:
            lv2 = MarketApi.Instance()
            rst = lv2.GetTransactionData(self._stock, 30)
            data = {"transaction": [i for i in rst]}
            ret_val = dumpUTF8Json(data)
            self._handler.write(ret_val)
        except QueryError as e:
            ret_val = dumpUTF8Json({"error": str(e)})
            self._handler.write(ret_val)
            self.complete()
        except:
            # TODO: all exception
            self.complete()
        else:
            self.complete()


class QueryTransactionDetailCmd(Command):

    def __init__(self, stock, handler):
        Command.__init__(self, handler)
        self._stock = stock
        self._handler = handler

    def execute(self):
        try:
            lv2 = MarketApi.Instance()
            rst = lv2.GetDetailTransactionData(self._stock, 30)
            data = {"transaction_detail": [i for i in rst]}
            ret_val = dumpUTF8Json(data)
            self._handler.write(ret_val)
        except QueryError as e:
            ret_val = dumpUTF8Json({"error": str(e)})
            self._handler.write(ret_val)
            self.complete()
        except:
            self.complete()
        else:
            self.complete()
