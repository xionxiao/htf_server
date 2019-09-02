# -*- coding: gbk -*-

import sys,time
sys.path.append("..")
from trade import TradeApi
from trade.stockpool import StockPool
from trade.query import c_query
from command import *
from common.resultbuffer import Result
from common.error import TradeError, QueryError
from common.utils import dumpUTF8Json,getMarketID
from common.cache import Cache

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

class GetPositionCmd(Command):
    def __init__(self, handler):
        Command.__init__(self, handler)
        self._api = TradeApi.Instance()
        self._handler = handler

    def execute(self):
        try:
            rst = c_query("股份")
            obj = {"position":rst.items}
            self._handler.write(dumpUTF8Json(obj))
        except Exception as e:
            err_str = dumpUTF8Json({"error":str(e)})
            self._handler.write(err_str)
        finally:
            self.complete()
            
class GetOrderListCmd(Command):
    def __init__(self, handler):
        Command.__init__(self, handler)
        self._api = TradeApi.Instance()
        self._handler = handler

    def execute(self):
        try:
            rst = c_query("可撤单")
            obj = {"orderlist":rst.items}
            self._handler.write(dumpUTF8Json(obj))
        except Exception as e:
            err_str = dumpUTF8Json({"error":str(e)})
            self._handler.write(err_str)
        finally:
            self.complete()

class GetDealsCmd(Command):
    def __init__(self, handler):
        Command.__init__(self, handler)
        self._api = TradeApi.Instance()
        self._handler = handler

    def execute(self):
        try:
            rst = c_query("当日成交")
            obj = {"deals":rst.items}
            self._handler.write(dumpUTF8Json(obj))
        except Exception as e:
            err_str = dumpUTF8Json({"error":str(e)})
            self._handler.write(err_str)
        finally:
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
        obj = {"request":
               {"cmd":"buy",
                "stock":self._stock,
                "price":self._price,
                "share":self._share
                }
               }
        try:
            res = self._api.Buy(self._stock, self._price, self._share)
            # TODO: 更丰富的返回内容: {"command": {comd: buy, stock:6000036, price:18.5, share:100}
            #                        "result": ...,
            #                        "error":
            obj["result"] = res[0]
            self._handler.write(dumpUTF8Json(obj))
        except TradeError as e:
            obj['error'] = str(e)
            err_str = dumpUTF8Json(obj)
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
        obj = {"request":
               {"cmd":"sell",
                "stock":self._stock,
                "price":self._price,
                "share":self._share
                }
               }
        try:
            res = self._api.Sell(self._stock, self._price, self._share)
            obj['result'] = res[0]
            self._handler.write(dumpUTF8Json(obj))
        except TradeError as e:
            obj['error'] = str(e)
            err_str = dumpUTF8Json(obj)
            self._handler.write(err_str)
        finally:
            self.complete()

class DirectShortCmd(Command):
    def __init__(self, stock, price, share, handler):
        Command.__init__(self, handler)
        self._api = TradeApi.Instance()
        self._stock = stock
        self._price = price
        self._share = share
        self._handler = handler

    def execute(self):
        obj = {"request":
               {"cmd":"direct_short",
                "stock":self._stock,
                "price":self._price,
                "share":self._share
                }
               }
        try:
            res = self._api.Short(self._stock, self._price, self._share)
            obj['result'] = res[0]
            self._handler.write(dumpUTF8Json(obj))
        except TradeError as e:
            obj['error'] = str(e)
            err_str = dumpUTF8Json(obj)
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
        obj = {"request":
               {"cmd":"short",
                "stock":self._stock,
                "price":self._price,
                "share":self._share
                }
               }
        try:
            self._sp.sync()
            i,c,s = self._sp.acquire(self._stock, self._share)
            if i:
                marketId = str(getMarketID(self._stock))
                if type(i) is list:
                    marketId = [marketId] * len(i)
                res = self._api.CancelOrder(marketId, i)
            else:
                obj['error'] = "acquire error: stock="+self._stock+" share="+str(self._share)
                self._handler.write(dumpUTF8Json(obj))
                return
            time.sleep(0.3)
            if s > 0:
                res = self._sp.fill(self._stock, s)
            res = self._api.Short(self._stock, self._price, self._share)
            obj["result"] = res[0]
            self._handler.write(dumpUTF8Json(obj))
        except TradeError as e:
            obj['error'] = str(e)
            err_str = dumpUTF8Json(obj)
            self._handler.write(err_str)
        finally:
            self.complete()

class CancelCmd(Command):
    def __init__(self, stock, orderId, handler):
        Command.__init__(self, handler)
        self._api = TradeApi.Instance()
        self._marketId = str(getMarketID(stock))
        self._stock = stock
        self._orderId = orderId
        self._handler = handler

    def execute(self):
        obj = {"request":
               {"cmd":"cancel",
                "orderId":self._orderId,
                "stock":self._stock,
                }
               }
        try:
            res = self._api.CancelOrder(self._marketId, self._orderId)
            obj["result"] = res[0]
            self._handler.write(dumpUTF8Json(obj))
        except TradeError as e:
            obj['error'] = str(e)
            err_str = dumpUTF8Json(obj)
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
    s = ShortCmd("000009", 11.75, 100, r)
    invoker.call(s)

