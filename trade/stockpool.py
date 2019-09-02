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
    """ 管理可交易的股票 """    
    def __init__(self):
        self._tradeApi = TradeApi.Instance()
        # structure of pooled stocks
        # { stock_code: 证券代码为键值
        #   {
        #       融券数量: 500
        #       融券上限: 1000
        #       订单列表: {order_id:share, order_id:share}
        #   }
        # }
        self._stock_pool = {}
        
    def acquire(self, stock, share):
        """ 获得相应数目股票, 返回撤消订单号,撤消订单股数，补充下单股数(涨停价)"""
        assert type(share) is int and share > 0
        assert share % 100 == 0
        if not self._stock_pool.has_key(stock):
            print u"股票池中没有对应股票"
            return [],[],0

        order_dict = self._stock_pool[stock]["订单列表"]
        sorted_dict = sorted(order_dict.items(), key=lambda d:d[1], reverse=True)
        
        keys = [ i[0] for i in sorted_dict ]
        values = [ i[1] for i in sorted_dict ]
        
        greater_pos = None
        out_key_list = []
        out_value_list = []
        if sum(values) < share:
            # raise exception
            print u"证券数量不足"
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

            # 列表中元素值小于目标值的位置
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
        """在股票池中增加单只股票"""
        if type(stock_code) is not list:
            stock_code = [stock_code]
        if type(upper_limit) is not list:
            upper_limit = [upper_limit]
        assert len(stock_code) == len(upper_limit)

        for i in range(len(stock_code)):
            _upper_limit = upper_limit[i]
            assert type(_upper_limit) is int and _upper_limit >= 0
            stock = {
                     "融券数量": 0,
                     "融券上限": _upper_limit,
                     "订单列表": {}
                    }
            self._stock_pool[stock_code[i]] = stock

    def getStocks(self):
        return self._stock_pool

    def addOrder(self, stock_code, order_id, order_price, order_share, order_type):
        """ 向订单列表增加订单 """
        pool = self._stock_pool

        harden_price = c_query("涨停价", stock_code)
        #print stock_code, harden_price, order_price, order_type
        if order_type == "融券卖出" and order_price == harden_price:
            if not pool.has_key(stock_code):
                pool[stock_code] = {"融券上限":order_share,
                                    "融券数量":order_share,
                                    "订单列表":{order_id:order_share}
                                    }
                return
            # 证券在股票池中
            pool = pool[stock_code]
            if not pool["订单列表"].has_key(order_id):
                pool["订单列表"][order_id] = order_share
                pool["融券数量"] += order_share
                if pool["融券数量"] > pool["融券上限"]:
                    pool["融券上限"] = pool["融券数量"]

    def removeOrder(self, order_id):
        for k,v in self._stock_pool.iteritems():
            if v["订单列表"].has_key(order_id):
                v["订单列表"].pop(order_id)
                return True
        return False
    
    def setUpperLimit(self, stock_code, max_shares):
        """ 设置股票池中某只股票存储上限 """
        assert type(max_shares) is int and max_shares > 0
        if self._stock_pool.has_key(stock_code):
            self._stock_pool[stock_code]["融券上限"] = max_shares

    def getUpperLimit(self, stock_code):
        """ 获取股票池中某只股票存储上限 """
        if self._stock_pool.has_key(stock_code):
            return self._stock_pool[stock_code]["融券上限"]
        else:
            return 0

    def getOrderList(self, stock_code):
        pass

    def sync(self):
        """ 与服务器同步股票池 """
        self._stock_pool = {}
        try:
            rst = c_query("可撤单")
        except QueryError as e:
            return

        # 整理重复订单 {证券代码：[订单信息]}
        for record in rst:
            stock_code = record["证券代码"]
            order_id = record["合同编号"]
            order_type = record["买卖标志"]
            ndigits = len(record["委托价格"].split('.')[1])
            order_price = round(float(record["委托价格"]), ndigits)
            order_share = int(float(record["委托数量"]))
            self.addOrder(stock_code,order_id,order_price,order_share,order_type)

        
    def fill(self, stock_code, share):
        """ 从服务器获取股票 """
        assert type(share) is int and share > 0
        assert isValidStockCode(stock_code)

        raising_price = c_query("涨停价", stock_code)
        try:
            rst = self._tradeApi.Short(stock_code, raising_price, share)
        except TradeError as e:
            return e.feedback
        return rst

    def lock(self, stock, share):
        """ 买单锁定股票 """
        pass

    def unLock(self, stock, share):
        """ 解锁股票 """
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
        print k,ss[k]["融券数量"],ss[k]["融券上限"],ss[k]["订单列表"]

    #print sp.acquire("600104",2200)
