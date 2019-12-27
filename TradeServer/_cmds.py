# -*- coding: utf8 -*-

import time
from hft.trade import TradeApi
from hft.trade.stockpool import StockPool
from hft.trade.query import c_query
from hft.common.command import *
from hft.common.resultbuffer import Result
from hft.common.error import TradeError, QueryError, CancelError, AcquireError
from hft.common.utils import dumpUTF8Json, getMarketID
from hft.common.cache import Cache


class GetStockPoolCmd(Command):

    def __init__(self, handler):
        Command.__init__(self, handler)
        self._handler = handler

    def execute(self):
        sp = StockPool.Instance()
        sp.sync()
        ss = sp.getStocks()
        obj = {"stockpool": ss}
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
            obj = {"position": rst.items}
            self._handler.write(dumpUTF8Json(obj))
        except Exception as e:
            err_str = dumpUTF8Json({"error": str(e)})
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
            obj = {"orderlist": rst.items}
            self._handler.write(dumpUTF8Json(obj))
        except Exception as e:
            err_str = dumpUTF8Json({"error": str(e)})
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
            obj = {"deals": rst.items}
            self._handler.write(dumpUTF8Json(obj))
        except Exception as e:
            err_str = dumpUTF8Json({"error": str(e)})
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
               {"cmd": "buy",
                "stock": self._stock,
                "price": self._price,
                "share": self._share
                }
               }
        try:
            res = self._api.Buy(self._stock, self._price, self._share)
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
               {"cmd": "sell",
                "stock": self._stock,
                "price": self._price,
                "share": self._share
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
               {"cmd": "direct_short",
                "stock": self._stock,
                "price": self._price,
                "share": self._share
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
               {"cmd": "short",
                "stock": self._stock,
                "price": self._price,
                "share": self._share
                }
               }
        try:
            res = self._sp.short_frompool(
                self._stock, self._price, self._share)
            obj["result"] = res[0]
        except CancelError as e:
            obj['error'] = str(e)
        except TradeError as e:
            obj['error'] = str(e)
        except AcquireError as e:
            obj['error'] = str(e)
        finally:
            self._handler.write(dumpUTF8Json(obj))
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
               {"cmd": "cancel",
                "orderId": self._orderId,
                "stock": self._stock,
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
