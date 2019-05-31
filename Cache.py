# -*- coding: gbk -*-
from Utils import *
from TradeApi import *

class Cache(Singleton):
    """ 缓存系统 """

    # structure of stock cache
    # { stock_code: 证券代码为键值
    #   {
    #       证券代码: 600036
    #       证券名称: 招商银行
    #       涨停价: 19.98
    #       昨收价: 18.16
    #   }
    # }
    _stock_cache = {}
    _tradeApi = None

    def __init__(self, api=None):
        if api:
            assert type(api) is TradeApi
        if not self._tradeApi and not api:
            raise Exception("Need create with TradeApi First")
        self._tradeApi = api

    def add(self, stock):
        rst = self._tradeApi.Query("行情", stock=stocks)

        ret_val = []
        for i in range(len(rst)):
            r = rst[i]
            if not r:
                ret_val.append(r)
                continue

            _stock_code = r["证券代码"][0]
            _stock_name = r["证券名称"][0]
            _closing_price = float(r["昨收价"][0])
            _harden_price = round_up_decimal_2(_closing_price*1.1)

            cache = {
                     "证券代码": _stock_code,
                     "证券名称": _stock_name,
                     "昨日收盘价": _closing_price,
                     "涨停价": _harden_price,
                    }
            self._stock_cache[_stock_code] = cache

        return ret_val

    def get(self, stock, variety):
        assert variety in ["证券代码","证券名称","昨日收盘价","涨停价"]
        if self._stock_cache.has_key(stock):
            return self._stock_cache[stock][variety]
        return None

    def __getitem__(self, stock):
        if self._stock_cache.has_key(stock):
            return self._stock_cache[stock][variety]
        return None

    def has_key(self, stock):
        return self._stock_cache.has_key(stock)

    def cacheMarginableStocks(self):
        """ 缓存可融证券的 证券代码，证券名称，昨收价，涨停价 """

        rst = self._tradeApi.Query("可融证券")
        if not rst:
            return rst
        stocks = rst[0]["证券代码"]
        self.add(stocks)
        return True


if __name__ == "__main__":
    api = TradeApi()
    if not api.isLogon():
        api.Open()
        rst = api.Logon("125.39.80.105", 443, "184039030", "326326")
        printd(rst)
    cache = Cache(api)
    print cache.has_key("1234")
    
