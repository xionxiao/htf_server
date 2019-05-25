# -*- coding: gbk -*-

from TradeApi import *
from Utils import *
import xlrd

class StockPool(object):
    """股票池"""

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
    
    def __init__(self, tradeApi):
        if not tradeApi.IsLogon():
            raise Exception("Need logon first")
        self._tradeApi = tradeApi
        self.__cacheStock()
        
    def acquire(self, stock, share):
        """ 获得相应数目股票, 返回撤消订单号和下单股数"""

        if stock not in self._stock_pool:
            return u"股票池中没有该股票"

        if not self._stock_pool[stock]["融券数量"] > share:
            return u"可用做空股票不足"
        order_list = self._stock_pool[stock]["订单列表"]
        print sorted(order_list.items(), key=lambda d: d[1]) 
            
        
    def __cacheStock(self, stocks=None):
        """ 缓存可融证券的 证券代码，证券名称，昨收价，涨停价 """

        if not stocks:
            rst = self._tradeApi.Query("可融证券")
            if not rst:
                return rst
            stocks = rst[0]["证券代码"]

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
    
    def addStock(self, stock_code, upper_limit):
        """在股票池中增加单只股票"""
        # 参数检查
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
                         "融券数量": 0,
                         "融券上限": _upper_limit,
                         "订单列表": {}
                        }
                self._stock_pool[stock_code[i]] = stock

    def getStock(self):
        return self._stock_pool

    def addOrder(self, stock_code, order_id, order_price, order_share, order_type):
        """ 向订单列表增加订单 """
        assert type(order_share) is int and order_share >= 0
        assert type(order_price) is float

        pool = self._stock_pool
        cache = self._stock_cache

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
        rst = self._tradeApi.Query("可撤单")
        if not rst:
            return rst

        # 无可撤订单
        order_stocks = {}
        if not rst[0]:
            return

        self.__cacheStock([ i[1] for i in rst[0] ])
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
        cache = self._stock_cache

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

    
