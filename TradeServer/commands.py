# -*- coding: gbk -*-

import sys
sys.path.append("..")
from trade import TradeApi
from command import *
from common.error import TradeError
from common.utils import dumpUTF8Json

class BuyCmdCommand):
    def __init__(self, api, stock, price, share, handler):
        Command.__init__(self, handler)
        self._api = api
        self._stock = stock
        self._price = price
        self._share = share
        self._handler = handler

    def execute(self):
        try:
            res = self._api.Buy(self._stock, self._price, self._share)
            obj = {"result": res}
            self._handler.write(dumpUTF8Json(obj))
        except TradeError as e:
            err_str = dumpUTF8Json({"error":str(e)})
            self._handler.write(err_str)
        finally:
            self._handler.onComplete(self)

class SellCmd(Command):
    def __init__(self, api, stock, price, share, handler):
        Command.__init__(self, handler)
        self._api = api
        self._stock = stock
        self._price = price
        self._share = share
        self._handler = handler

    def execute(self):
        try:
            res = self._api.Sell(self._stock, self._price, self._share)
            obj = {"result": res}
            self._handler.write(dumpUTF8Json(obj))
        except TradeError as e:
            err_str = dumpUTF8Json({"error":str(e)})
            self._handler.write(err_str)
        finally:
            self._handler.onComplete(self)

class ShortCmd(Command):
    def __init__(self, api, stock, price, share, handler):
        Command.__init__(self, handler)
        self._api = api
        self._stock = stock
        self._price = price
        self._share = share
        self._handler = handler

    def execute(self):
        try:
            res = self._api.Sell(self._stock, self._price, self._share)
            obj = {"result": res}
            self._handler.write(dumpUTF8Json(obj))
        except TradeError as e:
            err_str = dumpUTF8Json({"error":str(e)})
            self._handler.write(err_str)
        finally:
            self._handler.onComplete(self)

if __name__ == "__main__":
    api = TradeApi.Instance()
    if not api.isLogon():
        api.Logon("219.143.214.201", 7708, 0, "221199993903", "787878", version="2.19")
    class ResponseReceiver(Receiver):
        def write(self, msg):
            print msg
    r = ResponseReceiver()
    buy = SellCommand(api, "600036", 18.0, 100, r)
    buy.execute()

