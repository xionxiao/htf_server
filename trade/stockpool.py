# -*- coding: gbk -*-

from trade import TradeApi
from common.error import *
from common.utils import *
from query import c_query
import time

class StockPoolAcquireError(TradeError):
    pass

@Singleton
class StockPool():
    """ ����ɽ��׵Ĺ�Ʊ """    
    def __init__(self):
        self._tradeApi = TradeApi.Instance()
        # structure of pooled stocks
        # { stock_code: ֤ȯ����Ϊ��ֵ
        #   {
        #       ��ȯ����: 500
        #       ��ȯ����: 1000
        #       �����б�: {order_id:share, order_id:share}
        #   }
        # }
        self._stock_pool = {}
        
    def acquire(self, stock, share):
        """ �����Ӧ��Ŀ��Ʊ, ���س���������,�������������������µ�����(��ͣ��)"""
        assert type(share) is int and share > 0
        assert share % 100 == 0
        if not self._stock_pool.has_key(stock):
            print u"��Ʊ����û�ж�Ӧ��Ʊ"
            return [],[],0

        order_dict = self._stock_pool[stock]["�����б�"]
        sorted_dict = sorted(order_dict.items(), key=lambda d:d[1], reverse=True)
        
        keys = [ i[0] for i in sorted_dict ]
        values = [ i[1] for i in sorted_dict ]
        
        greater_pos = None
        out_key_list = []
        out_value_list = []
        if sum(values) < share:
            # raise exception
            print u"֤ȯ��������"
            return [],[],0
        for i in range(len(sorted_dict)):
            if not greater_pos:
                if values[i] == share:
                    out_key_list.append(keys[i])
                    out_value_list.append(values[i])
                    return out_key_list,out_value_list,0
                elif values[i] > share:
                    if i == len(values)-1:
                        out_key_list.append(keys[i])
                        out_value_list.append(values[i])
                        return out_key_list,out_value_list,values[i]-share
                    continue
                else:
                    greater_pos = i-1
                    s = sum(values[i:])
                    if s == share:
                        out_key_list = keys[i:]
                        out_value_list = values[i:]
                        return out_key_list,out_value_list,0
                    elif s < share:
                        out_key_list = keys[greater_pos]
                        out_value_list = values[greater_pos]
                        return out_key_list,out_value_list,values[greater_pos]-share
                    else:
                        share = share - values[i]
                        out_key_list.append(keys[i])
                        out_value_list.append(values[i])
                        continue

            # �б���Ԫ��ֵС��Ŀ��ֵ��λ��
            if share == values[i]:
                out_key_list.append(keys[i])
                out_value_list.append(values[i])
                return out_key_list,out_value_list,0
            elif share < values[i]:
                if i == len(values)-1:
                    out_key_list.append(keys[i])
                    out_value_list.append(values[i])
                    return out_key_list,out_value_list,values[i]-share
                continue
            else:
                share = share - values[i]
                out_key_list.append(keys[i])
                out_value_list.append(values[i])
                if share == 0:
                    return out_key_list,out_value_list,0

    def addStock(self, stock_code, upper_limit):
        """�ڹ�Ʊ�������ӵ�ֻ��Ʊ"""
        if type(stock_code) is not list:
            stock_code = [stock_code]
        if type(upper_limit) is not list:
            upper_limit = [upper_limit]
        assert len(stock_code) == len(upper_limit)

        for i in range(len(stock_code)):
            _upper_limit = upper_limit[i]
            assert type(_upper_limit) is int and _upper_limit >= 0
            stock = {
                     "��ȯ����": 0,
                     "��ȯ����": _upper_limit,
                     "�����б�": {}
                    }
            self._stock_pool[stock_code[i]] = stock

    def getStocks(self):
        return self._stock_pool

    def addOrder(self, stock_code, order_id, order_price, order_share, order_type):
        """ �򶩵��б����Ӷ��� """
        pool = self._stock_pool

        harden_price = c_query("��ͣ��", stock_code)
        #print stock_code, harden_price, order_price, order_type
        if order_type == "��ȯ����" and order_price == harden_price:
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

    def removeOrder(self, order_id):
        for k,v in self._stock_pool.iteritems():
            if v["�����б�"].has_key(order_id):
                v["�����б�"].pop(order_id)
                return True
        return False
    
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
        self._stock_pool = {}
        try:
            rst = c_query("�ɳ���")
        except QueryError as e:
            return

        # �����ظ����� {֤ȯ���룺[������Ϣ]}
        for record in rst:
            stock_code = record["֤ȯ����"]
            order_id = record["��ͬ���"]
            order_type = record["������־"]
            ndigits = len(record["ί�м۸�"].split('.')[1])
            order_price = round(float(record["ί�м۸�"]), ndigits)
            order_share = int(float(record["ί������"]))
            self.addOrder(stock_code,order_id,order_price,order_share,order_type)

        
    def fill(self, stock_code, share):
        """ �ӷ�������ȡ��Ʊ """
        assert type(share) is int and share > 0
        assert isValidStockCode(stock_code)

        raising_price = c_query("��ͣ��", stock_code)
        try:
            rst = self._tradeApi.Short(stock_code, raising_price, share)
        except TradeError as e:
            return e.feedback
        return rst

    def lock(self, stock, share):
        """ ��������Ʊ """
        pass

    def unLock(self, stock, share):
        """ ������Ʊ """
        pass

if __name__ == "__main__":
    api = TradeApi.Instance()
    if not api.isLogon():
        rst = api.Logon("219.143.214.201", 7708, 0, "221199993903", "787878", version="2.19")
    sp = StockPool.Instance()
    
    sp.sync()
    ss = sp.getStocks()
    print ss
    for k in ss:
        print k,ss[k]["��ȯ����"],ss[k]["��ȯ����"],ss[k]["�����б�"]

    #print sp.acquire("600104",2200)
