# -*- coding: gbk -*-

from ctypes import *
from Utils import *
from ResultBuffer import *
from ErrorExp import *
import datetime, time, numbers

@Singleton
class TradeApi():
    # 查询类型
    QUERY_TYPE = ("资金",  # 0
                  "股份",  # 1 
                  "当日委托",  # 2
                  "当日成交",  # 3
                  "可撤单",  # 4
                  "股东代码",  # 5
                  "融资余额",  # 6
                  "融券余额",  # 7
                  "可融证券"   # 8
                  )
    # 订单类型
    ORDER_TYPE = ("买入", # 0
                  "卖出", # 1
                  "融资买入", # 2
                  "融券卖出", # 3
                  "买券还券", # 4
                  "卖券还款", # 5
                  "现券还券", # 6
                  )
    # 历史委托类型
    HISTORY_QUERY_TYPE = ("历史委托", # 0
                          "历史成交", # 1
                          "交割单", # 2
                          )
    
    def __init__(self):
        self._clientId = -1
        self._ip = ""
        self._port = None
        self._shareholder = {"沪市":None, "深市":None} # 股东代码
        # When load fails this may throw WindowsError exception
        self._dll = windll.LoadLibrary("trade.dll")
        self.Open()

    def __del__(self):
        self.Logoff()
        self.Close()
        
    def Open(self):
        """ May throw AttributeError exception if dll not match """
        self._dll.OpenTdx()

    def Close(self):
        self._dll.CloseTdx()
    
    def Logon(self, ip, port, account, password, TxPassword="", version="9.01"):
        u""" 登录服务器 """
        assert isValidIpAddress(ip)
        assert type(port) is int
        assert type(account) is str
        assert type(password) is str
        
        rst = ResultBuffer()
        client = self._dll.Logon(ip, port, version, account, password, TxPassword, rst.ErrInfo)
        if client == -1:
            raise LogonError(ip, port, rst[0])
        self._clientId = client
        self._ip = ip
        self._port = port
        # 获得股东代码
        rst = self.QueryData(5)
        if rst[0]["资金帐号"] == "1":
            self._shareholder["沪市"] = rst[1]["股东代码"]
            self._shareholder["深市"] = rst[0]["股东代码"]
        else:
            self._shareholder["沪市"] = rst[0]["股东代码"]
            self._shareholder["深市"] = rst[1]["股东代码"]
    
    def Logoff(self):
        if self._clientId != -1:
            self._dll.Logoff(self._clientId)
            self._clientId = -1

    def isLogon(self):
        u""" 检查是否已登录 """
        # 如果 clientId 失效，在调用其他API时会抛出WindowsError异常， Error -1073741816
        return bool(self._clientId != -1)
    
    def QueryData(self, category):
        u""" 查询各种交易数据
             0资金  1股份   2当日委托  3当日成交    4可撤单   5股东代码  6融资余额   7融券余额  8可融证券
        """
        
        assert self.isLogon()
        assert type(category) is int
        assert category in range(len(self.QUERY_TYPE))
        
        res = ResultBuffer()
        self._dll.QueryData(self._clientId, category, res.Result, res.ErrInfo)
        if not res:
            raise QueryError(category, res[0])
        return res[0]

    def QueryDatas(self, categories):
        u""" 查询各种交易数据:
             categories is query type list.
             0资金  1股份   2当日委托  3当日成交    4可撤单   5股东代码  6融资余额   7融券余额  8可融证券
        """
        assert self.isLogon()
        assert type(categories) is list
        assert len(categories) > 0
        
        count = len(categories)
        for cat in categories:
            assert cat in range(9)
        _category = c_array(category, c_int)
        res = ResultBuffer(count)
        self._dll.QueryDatass(self._clientId, _category, count, res.Result, res.ErrInfo)
        if not res:
            raise BatchQueryError(categories, res.getResults())
        return res.getResults()

    def QueryHistoryData(self, histQueryType, startDate, endDate):
        u""" 查询历史交易数据：
             0历史委托  1历史成交   2交割单
             日期格式: 20140301
        """
        assert self.isLogon()
        assert category in range(len(self.HISTORY_QUERY_TYPE))
        assert isValidDate(startDate)
        assert isValidDate(endDate)
        
        res = ResultBuffer()
        self._dll.QueryHistoryData(self._clientId, histQueryType, startDate, endDate, res.Result, res.ErrInfo)
        if not res:
            raise QueryError(histQueryType, res[0], startDate=startDate, endDate=endDate)
        return res[0]

    def GetQuote(self, stocks):
        u""" 查询行情数据 """
        assert self.isLogon()
        assert type(stocks) in [str, list]
        
        if type(stocks) is list:
            count = len(stocks)
            # Fix Bug when only one command in banch
            if count == 1:
                return self.GetQuote(stocks[0])
            _stocks = c_array(stocks, c_char_p)
            res = ResultBuffer(count)
            self._dll.GetQuotes(self._clientId, _stocks, count, res.Result, res.ErrInfo)
            if not res:
                raise QueryError("quote", res.getResults(), stocks=stocks)
            return res.getResults()
        else:
            res = ResultBuffer()
            self._dll.GetQuote(self._clientId, stocks, res.Result, res.ErrInfo)
            if not res:
                raise BatchQueryError("quote", res[0], stock=stocks) 
            return res[0]

    # 获取股东代码
    def _getShareholderID(self, stock):
        market_id = getMarketID(stock, True)
        return self._shareholder[market_id]
    
    def SendOrder(self, category, stock, price, quantity, priceType=0, shareholder=''):
        u"""
        category:
            # 0买入
            # 1卖出
            # 2融资买入
            # 3融券卖出
            # 4买券还券
            # 5卖券还款
            # 6现券还券
        priceType:
            # 0上海限价委托 深圳限价委托
            # 1(市价委托)深圳对方最优价格
            # 2(市价委托)深圳本方最优价格
            # 3(市价委托)深圳即时成交剩余撤销
            # 4(市价委托)上海五档即成剩撤 深圳五档即成剩撤
            # 5(市价委托)深圳全额成交或撤销
            # 6(市价委托)上海五档即成转限价
         """
        
        # 参数检查
        assert self.isLogon()
        assert type(category) is int and category in range(7)
        assert type(priceType) is int and priceType in range(7)
        assert isValidStockCode(stock)
        assert isinstance(price, numbers.Number)
        assert type(quantity) is int and quantity > 0
        
        res = ResultBuffer()
        # 处理股东代码
        shareholder = self._getShareholderID(stock)
        self._dll.SendOrder(self._clientId, category, priceType, shareholder, stock, c_float(price), quantity, res.Result, res.ErrInfo)
        if not res:
            raise TradeError(category, stock, price, quantity, priceType, res[0])
        return res[0]

    def SendOrders(self, categories, stocks, prices, quantities, priceTypes=[0], shareholder=['']):
        u""" 批量下单接口 """
        assert self.isLogon()
        assert type(categories) is list
        assert type(stocks) is list
        assert type(prices) is list
        assert type(quantities) is list
        assert type(priceTypes) is list
        assert type(shareholder) is list
        
        count = len(categories)
        assert len(stocks)==count and len(prices)==count and len(quantities)==count

        if len(priceTypes) == 1:
            priceTypes = priceTypes * count
        for i in range(count):
            assert isValidStockCode(stocks[i])
            assert isinstance(prices[i], numbers.Number)
            assert type(quantities[i]) is int and quantities[i]>0
            assert type(priceTypes[i]) is int and priceTypes[i] in range(7)

        # Bug when only one command in banch
        if count == 1:
            res = self.SendOrder(categories[0], stocks[0], prices[0], quantities[0], priceTypes[0], shareholder[0])
            if not res:
                raise BatchTradeError(categories, stocks, prices, quantities, priceTypes, [res])
            return [res]
        
        _categories = c_array(categories, c_int)
        _stocks = c_array(stocks, c_char_p)
        _prices = c_array(prices, c_float)
        _quantities = c_array(quantities, c_int)
        _priceTypes = c_array(priceTypes, c_int)
        if len(shareholder) == 1:
            shareholder = []
            for i in stocks:
                shareholder.append(self._getShareholderID(i))
        
        _shareholder = c_array(shareholder, c_char_p)
        
        res = ResultBuffer(count)
        self._dll.SendOrders(self._clientId, _categories, _priceTypes, _shareholder, _stocks, _prices, _quantities, count, res.Result, res.ErrInfo)
        if not res:
            raise BatchTradeError(categories, stocks, prices, quantities, priceTypes, res.getResults())
        return res.getResults()
    
    def CancelOrder(self, orderId):
        assert self.isLogon()
        assert type(orderId) in [list, str]
        if type(orderId) is list:
            count = len(orderId)
            # Fix Bug when only one command in banch
            if count == 1:
                return self.CancelOrder(orderId[0])
            res = ResultBuffer(count)
            _orderId = c_array(orderId, c_char_p)
            self._dll.CancelOrders(self._clientId, _orderId, count, res.Result, res.ErrInfo)
            if not res:
                raise CancelError(res[0], order_id=orderId)
            return res.getResults()
        elif type(orderId) is str:
            res = ResultBuffer()
            self._dll.CancelOrder(self._clientId, orderId, res.Result, res.ErrInfo)
            if not res:
                raise CancelError(res.getResults(), order_id=orderId)
            return res[0]
            
    def Repay(self, amount):
        assert self.isLogon()
        res = ResultBuffer()
        self._dll.Repay(self._clientId, amount, res.Result, res.ErrInfo)
        if not res:
            raise RepayError(res[0], amount=amount)
        return res[0]

if __name__ == "__main__":
    api = TradeApi.Instance()
    #f = open('out.txt', 'w+')
    #import sys
    #sys.stdout=f
    try:
        if not api.isLogon():
            api.Logon("59.173.7.38", 7708, "184039030", "326326")
        rst = api.QueryData(5)
        print rst
##        rst = api.Query("资金")
##        printd(rst)
##        print rst.attr[3] == "冻结资金"

##        print u"======== 股份"
##        rst = api.Query("股份")
##       
##        printd(rst)
##        print u"======== 当日委托"
##        printd(api.Query("当日委托"))
##        print u"======== 当日成交"
##        printd(api.Query("当日成交"))
##        print u"======== 可撤单"
##        printd(api.Query("可撤单"))
##        print u"======== 股东代码"
##        printd(api.Query("股东代码"))
##        print u"======== 融资余额"
##        printd(api.Query("融资余额"))
##        #print u"======== 融券余额"
##        #printd(api.Query("融券余额")) # 系统暂不支持该功能
##        print u"======== 可融证券"
##        printd(api.Query("可融证券"))
##        print "========"

        #rst = api.QueryHistoryData(0, "20150429", "20150504")
        #printd(rst)
        #printd(api.Query("历史委托", "20150429", "20150504")[0])
        #printd(api.Query("历史成交", "20150429", "20150504")[0])
        #printd(api.Query("交割单", startDate="20150429", endDate="20150504")[0])

        #rst = api.Query("当前价", stock="000002")
        #printd(rst)

        #print api.Repay("1000")
        #rst = api.CancelOrder(["1799","1798"])
        #print rst
        
        #rst = api.SendOrder(3, "000655", 0.22, 100)
        #print rst
        #print api.SendOrders([3,3,3], ["000655", "000625","600005"], [0.22, 0.11,0.4], [100,100,200])
        #print api.Buy("000690", 18.8, 100)
        #print api.Sell("000690", 10.10, 100)
        #print api.Short("600005", 6.4, 100)
    except ErrorExp as e:
        print "!!!!!!!!!!!!!!!!!!!!!"
        print e.feedback
    finally:
        print "Log off"
        api.Logoff()

    #f.close()
