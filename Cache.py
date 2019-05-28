# -*- coding: gbk -*-

class Cache(object):
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

    def __init__(self, tradeApi):
        if not tradeApi.IsLogon():
            raise Exception("Need logon first")
        self._tradeApi = tradeApi

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


