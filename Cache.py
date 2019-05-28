# -*- coding: gbk -*-

class Cache(object):
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

    def __init__(self, tradeApi):
        if not tradeApi.IsLogon():
            raise Exception("Need logon first")
        self._tradeApi = tradeApi

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


