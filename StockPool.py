# -*- coding: gbk -*-

from TradeApi import *
from Utils import *
import xlrd

class StockPool(object):
    """��Ʊ��"""

    _tradeApi = None
    # structure of pooled stocks
    # { stock_code: ֤ȯ����Ϊ��ֵ
    #   {
    #       ��ȯ����: 500
    #       ��ȯ����: 1000
    #       �����б�: {order_id:share, order_id:share}
    #   }
    # }
    _stock_pool = {}
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
    
    def __init__(self, tradeApi):
        if not tradeApi.IsLogon():
            raise Exception("Need logon first")
        self._tradeApi = tradeApi
        self.__cacheStock()
        
    def acquire(self, stock, share):
        """ �����Ӧ��Ŀ��Ʊ, ���س��������ź��µ�����"""
        assert num % 100 == 0
        if not self._stock_pool.has_key(stock):
            return u"��Ʊ����û�иù�Ʊ"

        order_dict = self._stock_pool[stock]["�����б�"]
        sorted_order_dict = sorted(order_dict.items(), key=lambda d:d[1], reverse=True)
        
        keys = [ i[0] for i in sorted_dict ]
        values = [ i[1] for i in sorted_dict ]
        
        greater_pos = None
        out_key_list = []
        out_value_list = []
        if sum(values) < num:
            return u"֤ȯ��������"
        for i in range(len(sorted_dict)):
            if not greater_pos:
                if values[i] == num:
                    out_key_list.append(keys[i])
                    out_value_list.append(values[i])
                    return out_key_list,out_value_list,0
                elif values[i] > num:
                    if i == len(values)-1:
                        out_key_list.append(keys[i])
                        out_value_list.append(values[i])
                        return out_key_list,out_value_list,values[i]-num
                    continue
                else:
                    greater_pos = i-1
                    s = sum(values[i:])
                    if s == num:
                        out_key_list = keys[i:]
                        out_value_list = values[i:]
                        return out_key_list,out_value_list,0
                    elif s < num:
                        out_key_list = keys[greater_pos]
                        out_value_list = values[greater_pos]
                        return out_key_list,out_value_list,values[greater_pos]-num
                    else:
                        num = num - values[i]
                        out_key_list.append(keys[i])
                        out_value_list.append(values[i])
                        continue

            # �б���Ԫ��ֵС��Ŀ��ֵ��λ��
            if num == values[i]:
                out_key_list.append(keys[i])
                out_value_list.append(values[i])
                return out_key_list,out_value_list,0
            elif num < values[i]:
                if i == len(values)-1:
                    out_key_list.append(keys[i])
                    out_value_list.append(values[i])
                    return out_key_list,out_value_list,values[i]-num
                continue
            else:
                num = num - values[i]
                out_key_list.append(keys[i])
                out_value_list.append(values[i])
                if num == 0:
                    return out_key_list,out_value_list,0
            
        
    def __cacheStock(self, stocks=None):
        """ �������֤ȯ�� ֤ȯ���룬֤ȯ���ƣ����ռۣ���ͣ�� """

        if not stocks:
            rst = self._tradeApi.Query("����֤ȯ")
            if not rst:
                return rst
            stocks = rst[0]["֤ȯ����"]

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
    
    def addStock(self, stock_code, upper_limit):
        """�ڹ�Ʊ�������ӵ�ֻ��Ʊ"""
        # �������
        if type(stock_code) is not list:
            stock_code = [stock_code]
        if type(upper_limit) is not list:
            upper_limit = [upper_limit]
        assert len(stock_code) == len(upper_limit)

        for i in range(len(stock_code)):
            if self._stock_cache.has_key(stock_code[i]):
                _upper_limit = upper_limit[i]
                assert type(_upper_limit) is int and _upper_limit >= 0
                stock = {
                         "��ȯ����": 0,
                         "��ȯ����": _upper_limit,
                         "�����б�": {}
                        }
                self._stock_pool[stock_code[i]] = stock

    def getStock(self):
        return self._stock_pool

    def addOrder(self, stock_code, order_id, order_price, order_share, order_type):
        """ �򶩵��б����Ӷ��� """
        assert type(order_share) is int and order_share >= 0
        assert type(order_price) is float

        pool = self._stock_pool
        cache = self._stock_cache

        if not cache.has_key(stock_code):
            return u"�������ǿ���֤ȯ"

        if order_type == "��ȯ����" and order_price == cache[stock_code]["��ͣ��"]:
            if not pool.has_key(stock_code):
                pool[stock_code] = {"��ȯ����":order_share,
                                    "��ȯ����":order_share,
                                    "�����б�":{order_id:order_share}
                                    }
                return
            # ֤ȯ�ڹ�Ʊ����
            pool = pool[stock_code]
            if not pool["�����б�"].has_key(order_id):
                pool["�����б�"][order_id] = order_share
                pool["��ȯ����"] += order_share
                if pool["��ȯ����"] > pool["��ȯ����"]:
                    pool["��ȯ����"] = pool["��ȯ����"]
    
    def setUpperLimit(self, stock_code, max_shares):
        """ ���ù�Ʊ����ĳֻ��Ʊ�洢���� """
        assert type(max_shares) is int and max_shares > 0
        if self._stock_pool.has_key(stock_code):
            self._stock_pool[stock_code]["��ȯ����"] = max_shares

    def getUpperLimit(self, stock_code):
        """ ��ȡ��Ʊ����ĳֻ��Ʊ�洢���� """
        if self._stock_pool.has_key(stock_code):
            return self._stock_pool[stock_code]["��ȯ����"]
        else:
            return 0

    def getOrderList(self, stock_code):
        pass

    def sync(self):
        """ �������ͬ����Ʊ�� """
        rst = self._tradeApi.Query("�ɳ���")
        if not rst:
            return rst

        # �޿ɳ�����
        order_stocks = {}
        if not rst[0]:
            return

        self.__cacheStock([ i[1] for i in rst[0] ])
        # �����ظ����� {֤ȯ���룺[������Ϣ]}
        for record in rst[0]:
            stock_code = record[1]
            order_id = record[9]
            order_type = record[13]
            order_price = round_up_decimal_2(float(record[7]))
            order_share = int(float(record[8]))
            self.addOrder(stock_code,order_id,order_price,order_share,order_type)
            

    def fillAll(self):
        pool = self._stock_pool
        cache = self._stock_cache

        stock_code = pool.keys()
        stock_share = [ pool[i]["��ȯ����"] for i in stock_code ]

        rst = self._tradeApi.Query("����֤ȯ")
        if not rst:
            return rst

        _stock_code = []
        _harden_price = []
        _stock_share = []
        for s in stock_code:
            if s in rst[0]['֤ȯ����']:
                index = rst[0]['֤ȯ����'].index(s)
                stock_info = rst[0][index]
                _stock_code.append(s)
                _harden_price.append(cache[s]["��ͣ��"])
                _marginable_share = int(float(stock_info[2])/100)*100
                _upper_limit = pool[s]["��ȯ����"]
                _stock_share.append(min(_marginable_share, _upper_limit))

        rst = self._tradeApi.SendOrders([3]*len(_stock_code), _stock_code, _harden_price, _stock_share)
        if not rst:
            printd(rst)
            return rst

        
    def fill(self, stock_code, share):
        """ �ӷ�������ȡ��Ʊ """
        assert type(share) is int and share > 0
        
        if not self._stock_pool.has_key(stock_code):
            return u"û�п��ڹ�Ʊ��" + stock_code
        
        rst = self._tradeApi.Query("����֤ȯ")
        if not rst:
            return rst

        # ����֤ȯ��Ϣ���ַ����б�
        stock_info = None
        if stock_code in rst[0]['֤ȯ����']:
            index = rst[0]['֤ȯ����'].index(stock_code)
            stock_info = rst[0][index]

        if not stock_info:
            return u"û�ҵ���Ӧ��Ʊ"

        _stock_code = stock_info[0]
        _stock_name = stock_info[1]
        _harden_price = self._stock_pool[_stock_code]["��ͣ��"]
        # ����֤ȯ���������뵽100�ı���
        _marginable_share = int(float(stock_info[2])/100)*100
        _share = min(int(share/100)*100, _marginable_share)

        rst = self._tradeApi.Short(_stock_code, _harden_price, _share)
        if not rst:
            return rst

if __name__ == "__main__":
    #print grabStocks('05a.xls')
    api = TradeApi()
    api.Open()
    rst = api.Logon("125.39.80.105", 443, "184039030", "326326")
    sp = StockPool(api)
    
    xls = xlrd.open_workbook('05a.xls')
    table = xls.sheets()[0]
    stocks = [i.encode() for i in table.col_values(0)]
    shares = [int(i) for i in table.col_values(1)]
    #sp.addStock(stocks, shares)
    sp.sync()
    print sp.acquire('002294', 1000)
    printd([sp.getStock()])

    
