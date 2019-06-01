# -*- coding: gbk -*-

from TradeApi import *
from Utils import *
from Cache import *
import xlrd
import time

class StockPool(Singleton):
    """ 管理可交易的股票 """

    _tradeApi = None
    # structure of pooled stocks
    # { stock_code: 证券代码为键值
    #   {
    #       融券数量: 500
    #       融券上限: 1000
    #       订单列表: {order_id:share, order_id:share}
    #   }
    # }
    _stock_pool = {}
    _cache = None
    
    def __init__(self, tradeApi=None):
        if not self._tradeApi and not tradeApi:
            raise Exception("Need create with TradeApi first")
        self._tradeApi = tradeApi
        self._cache = Cache(tradeApi)
        
    def acquire(self, stock, share):
        """ 获得相应数目股票, 返回撤消订单号和下单股数"""
        assert type(share) is int and share > 0
        assert share % 100 == 0
        if not self._stock_pool.has_key(stock):
            print u"股票池中没有该股票"
            return [],[],0

        order_dict = self._stock_pool[stock]["订单列表"]
        sorted_dict = sorted(order_dict.items(), key=lambda d:d[1], reverse=True)
        
        keys = [ i[0] for i in sorted_dict ]
        values = [ i[1] for i in sorted_dict ]
        
        greater_pos = None
        out_key_list = []
        out_value_list = []
        if sum(values) < share:
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
        # 参数检查
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
        assert type(order_share) is int and order_share >= 0
        assert type(order_price) is float

        pool = self._stock_pool
        cache = self._cache

        if not cache.has_key(stock_code):
            return u"订单不是可融证券"

        if order_type == "融券卖出" and order_price == cache[stock_code]["涨停价"]:
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
        rst = self._tradeApi.Query("可撤单")
        if not rst:
            return rst

        # 无可撤订单
        order_stocks = {}
        if not rst[0][0]:
            return
        
        self._cache.add(rst[0]["证券代码"])
        # 整理重复订单 {证券代码：[订单信息]}
        for record in rst[0]:
            stock_code = record[1]
            order_id = record[9]
            order_type = record[13]
            order_price = round_up_decimal_2(float(record[7]))
            order_share = int(float(record[8]))
            self.addOrder(stock_code,order_id,order_price,order_share,order_type)
            

    def fillAll(self):
        pool = self._stock_pool
        cache = self._cache

        stock_code = pool.keys()
        stock_share = [ pool[i]["融券上限"] for i in stock_code ]

        rst = self._tradeApi.Query("可融证券")
        if not rst:
            return rst

        _stock_code = []
        _harden_price = []
        _stock_share = []
        for s in stock_code:
            if s in rst[0]['证券代码']:
                index = rst[0]['证券代码'].index(s)
                stock_info = rst[0][index]
                _stock_code.append(s)
                _harden_price.append(cache[s]["涨停价"])
                _marginable_share = int(float(stock_info[2])/100)*100
                _upper_limit = pool[s]["融券上限"]
                _stock_share.append(min(_marginable_share, _upper_limit))

        rst = self._tradeApi.SendOrders([3]*len(_stock_code), _stock_code, _harden_price, _stock_share)
        if not rst:
            printd(rst)
            return rst

        
    def fill(self, stock_code, share):
        """ 从服务器获取股票 """
        assert type(share) is int and share > 0
        
        if not self._stock_pool.has_key(stock_code):
            return u"没有可融股票：" + stock_code
        
        rst = self._tradeApi.Query("可融证券")
        if not rst:
            return rst

        # 可融证券信息（字符串列表）
        stock_info = None
        if stock_code in rst[0]['证券代码']:
            index = rst[0]['证券代码'].index(stock_code)
            stock_info = rst[0][index]

        if not stock_info:
            return u"没找到相应股票"

        _stock_code = stock_info[0]
        _stock_name = stock_info[1]
        _harden_price = self._stock_pool[_stock_code]["涨停价"]
        # 可融证券数量，舍入到100的倍数
        _marginable_share = int(float(stock_info[2])/100)*100
        _share = min(int(share/100)*100, _marginable_share)

        rst = self._tradeApi.Short(_stock_code, _harden_price, _share)
        if not rst:
            return rst

    def lock(self, stock, share):
        """ 买单锁定股票 """
        pass

    def unLock(self, stock, share):
        """ 解锁股票 """
        pass

if __name__ == "__main__":
    #print grabStocks('05a.xls')
    api = TradeApi()
    if not api.isLogon():
        api.Open()
        rst = api.Logon("125.39.80.105", 443, "184039030", "326326")
    sp = StockPool(api)
    
    #xls = xlrd.open_workbook('05a.xls')
    #table = xls.sheets()[0]
    #stocks = [i.encode() for i in table.col_values(0)]
    #shares = [int(i) for i in table.col_values(1)]
    #sp.addStock(stocks, shares)
    sp.sync()
    printd([sp.getStocks()])
    print "======"
    printd([sp.getStocks()['002294']])

##    for i in range(1,3):
##        sp.sync()
##        printd([sp.getStock()['002294']])
##        
##        xx = i * 100
##        pr = 41.73
##        c,d,e = sp.acquire('002294', xx)
##        print c
##        print d
##        print e
##        if c:
##            printd(api.CancelOrder(c))
##            time.sleep(0.5)
##            if e == 0:
##                printd(api.Short('002294', pr, xx))
##            else:
##                printd(api.SendOrders([3,3],['002294','002294'],[pr,41.76], [xx, e]))
##            for i in c:
##                sp.removeOrder(i)
##
##            printd([sp.getStock()['002294']])
##            time.sleep(1)
##        else:
##            print u"下单失败",xx,c,d,e
