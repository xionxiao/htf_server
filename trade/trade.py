# -*- coding: gbk -*-

from ctypes import *
import sys,os
sys.path.append("..")
from common.error import *
from common.utils import *
from common.resultbuffer import *
import datetime, time, numbers

@Singleton
class TradeApi():
    def __init__(self):
        self._clientId = -1
        self._ip = ""
        self._port = None
        self._shareholder = {"沪市":None, "深市":None} # 股东代码
        # When load fails this may throw WindowsError exception
        path = os.path.split(os.path.realpath(__file__))[0]
        self._dll = windll.LoadLibrary(path + "\\trade_yinhe.dll")
        self.Open()

    def __del__(self):
        self.Logoff()
        self.Close()
        
    def Open(self):
        """ May throw AttributeError exception if dll not match """
        self._dll.OpenTdx()

    def Close(self):
        self._dll.CloseTdx()
    
    def Logon(self, ip, port, branch, account, password, tradeAccount="", TxPassword="", version="9.01"):
        u""" 登录服务器 """
        assert isValidIpAddress(ip)
        assert type(port) is int
        assert type(account) is str
        assert type(password) is str
        assert type(branch) is int
        assert type(tradeAccount) is str

        if tradeAccount == "":
            tradeAccount = account
        rst = ResultBuffer()
        client = self._dll.Logon(ip, c_short(port), version, c_short(branch), account, tradeAccount, password, TxPassword, rst.ErrInfo)
        if client == -1:
            raise LogonError(ip, port, rst[0])
        self._clientId = client
        self._ip = ip
        self._port = port
        # 获得股东代码
        rst = self.QueryData(5)
        if rst[0]["股东代码"][0] == "E":
            self._shareholder["沪市"] = rst[0]["股东代码"]
            self._shareholder["深市"] = rst[1]["股东代码"]
        elif rst[0]["股东代码"][0] == "0":
            self._shareholder["沪市"] = rst[1]["股东代码"]
            self._shareholder["深市"] = rst[0]["股东代码"]
        else:
            raise LogonError(ip, port, rst, extra="wrong shareholder")
    
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
        assert category in range(9) # 0-8
        
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
            assert cat in range(9) # 0-8
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
        assert histQueryType in range(3) # 0-3
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
        assert type(category) is int and category in range(7) # 0-6
        assert type(priceType) is int and priceType in range(7) # 0-6
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
                raise BatchCancelError(res[0], order_id=orderId)
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

    def Buy(self, zqdm, price, share):
        return self.SendOrder(0, zqdm, price, share)

    def Sell(self, zqdm, price, share):
        return self.SendOrder(1, zqdm, price, share)

    def Short(self, zqdm, price, share):
        return self.SendOrder(3, zqdm, price, share)

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
    
    # 历史委托类型
    HISTORY_QUERY_TYPE = ("历史委托", # 0
                          "历史成交", # 1
                          "交割单", # 2
                          )
        
    def Query(self, u_str, *args, **kwargs):
        u""" 交易信息：
                  "资金"       0
                  "股份"       1
                  "当日委托"    2
                  "当日成交"    3
                  "可撤单"     4
                  "股东代码"    5
                  "融资余额"    6
                  "融券余额"    7
                  "可融证券"    8

           历史委托： 参数 -- startTime=20150512, endTime=20150513
                  "历史委托"    11
                  "历史成交"    12
                  "交割单"      13

           五档行情：  参数 -- stock="000002"
                  "行情"     21
                  "昨收价"    22
                  "今开价"    23
                  "当前价"    24
                  "涨停价"    25
        """
        if u_str in self.QUERY_TYPE:
            x = self.QUERY_TYPE.index(u_str)
            return self.QueryData(x)
        elif u_str in self.HISTORY_QUERY_TYPE:
            x = self.HISTORY_QUERY_TYPE.index(u_str)
            if len(args) == 0 and kwargs['startDate'] and kwargs['endDate']:
                return self.QueryHistoryData(x, kwargs['startDate'], kwargs['endDate'])
            elif len(args) == 2:
                return self.QueryHistoryData(x, args[0], args[1])
            else:
                return None
        elif u_str == "行情":
            if len(args) == 1:
                return self.GetQuote(args[0])
            elif len(args) == 0 and kwargs['stock']:
                return self.GetQuote(kwargs['stock'])
        
if __name__ == "__main__":
    api = TradeApi.Instance()
    #f = open('out.txt', 'w+')
    #import sys
    #sys.stdout=f
    try:
        if not api.isLogon():
            api.Logon("219.143.214.201", 7708, 0, "221199993903", "787878", version="2.19")
        rst = api.QueryData(5)
        print(rst)
        rst = api.Query("资金")
        print(rst)
        print(rst.attr[4] == "冻结资金")
        print(u"======== 股份")
        rst = api.Query("股份")
        print(rst)
        print(u"======== 当日委托")
        print(api.Query("当日委托"))
        print(u"======== 当日成交")
        print(api.Query("当日成交"))
        print(u"======== 可撤单")
        rst = api.Query("可撤单")
        print(rst)
        print(u"======== 股东代码")
        print(api.Query("股东代码"))
        print(u"======== 融资余额")
        print(api.Query("融资余额"))
        #print(u"======== 融券余额")
        #print(api.Query("融券余额")) # 系统暂不支持该功能
        print(u"======== 可融证券")
        print(api.Query("可融证券"))

        print(u"======== 历史委托")
        rst = api.QueryHistoryData(0, "20150429", "20150504")
        print(rst)
        rst = api.Query("历史委托", "20150708", "20150709")
        print(len(rst))
        print(u"======== 历史成交")
        print(api.Query("历史成交", "20150429", "20150501"))
        print(u"======== 交割单")
        print(api.Query("交割单", startDate="20150429", endDate="20150501"))

        print(u"======== 行情")
        rst = api.Query("行情", "000002")
        print(rst)

        #print api.Repay("1000")
        #rst = api.CancelOrder(["1799","1798"])
        #print rst
        
        #rst = api.SendOrder(3, "000655", 0.22, 100)
        #print rst
        #print api.SendOrders([3,3,3], ["000655", "000625","600005"], [0.22, 0.11, 0.4], [100,100,200])
        #print api.Buy("000690", 18.8, 100)
        #print api.Sell("000690", 10.10, 100)
        #print api.Short("600005", 6.4, 100)
    except ErrorException as e:
        print "!!!!!!!!!!!!!!!!!!!!!"
        print e.feedback
    finally:
        print "Log off"
        api.Logoff()

    #f.close()
