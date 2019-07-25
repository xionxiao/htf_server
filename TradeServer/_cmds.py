# -*- coding: gbk -*-

import sys
sys.path.append("..")
from trade import TradeApi
from trade.stockpool import StockPool
from command import *
from common.error import TradeError
from common.utils import dumpUTF8Json

class GetStockPoolCmd(Command):
    def __init__(self, handler):
        Command.__init__(self, handler)
        self._handler = handler

    def execute(self):
        sp = StockPool.Instance()
        sp.sync()
        ss = sp.getStocks()
        obj = {"stockpool":ss}
        self._handler.write(dumpUTF8Json(obj))
        self.complete()

class BuyCmd(Command):
    def __init__(self, stock, price, share, handler):
        Command.__init__(self, handler)
        self._api = TradeApi.Instance()
        self._stock = stock
        self._price = price
        self._share = share
        self._handler = handler

    def execute(self):
        try:
            res = self._api.Buy(self._stock, self._price, self._share)
            obj = {"result": res[0]}
            self._handler.write(dumpUTF8Json(obj))
        except TradeError as e:
            err_str = dumpUTF8Json({"error":str(e)})
            self._handler.write(err_str)
        finally:
            self.complete()

class SellCmd(Command):
    def __init__(self, stock, price, share, handler):
        Command.__init__(self, handler)
        self._api = TradeApi.Instance()
        self._stock = stock
        self._price = price
        self._share = share
        self._handler = handler

    def execute(self):
        try:
            res = self._api.Sell(self._stock, self._price, self._share)
            obj = {"result": res[0]}
            self._handler.write(dumpUTF8Json(obj))
        except TradeError as e:
            err_str = dumpUTF8Json({"error":str(e)})
            self._handler.write(err_str)
        finally:
            self.complete()

class ShortCmd(Command):
    def __init__(self, stock, price, share, handler):
        Command.__init__(self, handler)
        self._api = TradeApi.Instance()
        self._sp = StockPool.Instance()
        self._stock = stock
        self._price = price
        self._share = share
        self._handler = handler

    def execute(self):
        try:
            self._sp.sync()
            i,c,s = self._sp.acquire(self._stock, self._share)
            print i,c,s
            res = self._api.CancelOrder("15")
            print res
            time.sleep(1)
            res = self._sp.fill(self,_stock, s)
            print res
            res = self._api.Short(self._stock, self._price, self._share)
            print res
            obj = {"result": res[0]}
            self._handler.write(dumpUTF8Json(obj))
        except TradeError as e:
            err_str = dumpUTF8Json({"error":str(e)})
            self._handler.write(err_str)
        finally:
            self.complete()


if __name__ == "__main__":
    api = TradeApi.Instance()
    if not api.isLogon():
        api.Logon("219.143.214.201", 7708, 0, "221199993903", "787878", version="2.19")
    class ResponseReceiver(Receiver):
        def write(self, msg):
            print msg
    
    r = ResponseReceiver()
    invoker = Invoker()
    #buy = SellCmd("600036", 18.0, 100, r)
    s = ShortCmd("000401", 13.30, 100, r)
    invoker.call(s)

