# -*- coding: gbk -*-
from Utils import *
from TradeApi import *

class Cache(Singleton):
    """ ����ϵͳ """

    # structure of stock cache
    # { stock_code: ֤ȯ����Ϊ��ֵ
    #   {
    #       ֤ȯ����: 600036
    #       ֤ȯ����: ��������
    #       ��ͣ��: 19.98
    #       ���ռ�: 18.16
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
        rst = self._tradeApi.Query("����", stock=stocks)

        ret_val = []
        for i in range(len(rst)):
            r = rst[i]
            if not r:
                ret_val.append(r)
                continue

            _stock_code = r["֤ȯ����"][0]
            _stock_name = r["֤ȯ����"][0]
            _closing_price = float(r["���ռ�"][0])
            _harden_price = round_up_decimal_2(_closing_price*1.1)

            cache = {
                     "֤ȯ����": _stock_code,
                     "֤ȯ����": _stock_name,
                     "�������̼�": _closing_price,
                     "��ͣ��": _harden_price,
                    }
            self._stock_cache[_stock_code] = cache

        return ret_val

    def get(self, stock, variety):
        assert variety in ["֤ȯ����","֤ȯ����","�������̼�","��ͣ��"]
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
        """ �������֤ȯ�� ֤ȯ���룬֤ȯ���ƣ����ռۣ���ͣ�� """

        rst = self._tradeApi.Query("����֤ȯ")
        if not rst:
            return rst
        stocks = rst[0]["֤ȯ����"]
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
    
