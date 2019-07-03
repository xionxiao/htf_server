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
    # 股东代码 长江证券
    GDDM_CJZQ = { '深市':'0603467002', '沪市':'E035674151' }
    
    # 股东代码 国泰君安
    GDDM_GTJA = { '深市':'0603710116', '沪市':'E037015793' }

    GDDM_TYPE = GDDM_CJZQ
    
    def __init__(self):
        self._clientId = -1
        self._ip = ""
        self._port = None
        self._stock_holder = None # 股东代码
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
            raise LogonError,"Logon failed: " + rst.ErrInfo.value
        self._clientId = client
        self._ip = ip
        self._port = port
        # TODO: 获得股东代码
        # rst = self.QueryData(5)

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
            # Todo: 更好的QueryException构造函数
            raise QueryError
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
            # TODO: 处理是哪个查询失败
            raise QueryError
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
            # TODO: more information
            raise QueryError
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
                # TODO: 详细的错误信息
                raise QueryError
            return res.getResults()
        else:
            res = ResultBuffer()
            self._dll.GetQuote(self._clientId, stocks, res.Result, res.ErrInfo)
            if not res:
                # TODO: "详细的错误信息"
                raise QueryError
            return res[0]

    def SendOrder(self, category, stock, price, quantity, priceType=0, gddm=''):
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
        
        # TODO: 参数检查
        assert self.isLogon()
        assert type(category) is int and category in range(7)
        assert type(priceType) is int and priceType in range(7)
        assert isValidStockCode(stock)
        assert isinstance(price, numbers.Number)
        assert type(quantity) is int and quantity > 0
        
        res = ResultBuffer()
        # TODO: 自动处理股东代码
        if not gddm:
            if stock[0] == '6':
                gddm = self.GDDM_TYPE['沪市']
            else:
                gddm = self.GDDM_TYPE['深市']
        self._dll.SendOrder(self._clientId, category, priceType, gddm, stock, c_float(price), quantity, res.Result, res.ErrInfo)
        if not res:
            # TODO: TradeException详细信息
            raise TradeError
        return res[0]

    def SendOrders(self, categories, stocks, prices, quantities, priceTypes=[0], gddm=['']):
        assert self.isLogon()
        assert type(categories) is list
        assert type(stocks) is list
        assert type(prices) is list
        assert type(quantities) is list
        assert type(priceType) is list
        assert type(gddm) is list
        
        count = len(categories)
        assert len(stocks)==count and len(price)==count and len(quantity)==count

        for i in range(count):
            assert isValidStockCode(stocks[i])
            assert isinstance(prices[i], numbers.Number)
            assert type(quantities[i]) is int and quantities[i]>0
            assert type(priceTypes[i]) is int and priceType[i] in range(7)

        # Bug when only one command in banch
        if count == 1:
            return [self.SendOrder(categories[0], zqdm[0], price[0], quantity[0], priceTypes[0], gddm[0])]
        
        _categories = c_array(categories, c_int)
        _stocks = c_array(stocks, c_char_p)
        _prices = c_array(prices, c_float)
        _quantities = c_array(quantities, c_int)
        _priceTypes = c_array(pirceTypes, c_int)
        if not gddm:
            gddm = []
            for i in zqdm:
                if i[0] == '6':
                    gddm.append(self.GDDM_TYPE['沪市'])
                else:
                    gddm.append(self.GDDM_TYPE['深市'])
        _gddm = c_array(gddm, c_char_p)
        
        res = ResultBuffer(count)
        self._dll.SendOrders(self._clientId, _categories, _priceTypes, _gddm, _stocks, _prices, _quantities, count, res.Result, res.ErrInfo)
        if not res:
            # TODO: TradeException
            raise TradeError
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
                raise TradeError
            return res.getResults()
        elif type(orderId) is str:
            res = ResultBuffer()
            self._dll.CancelOrder(self._clientId, orderId, res.Result, res.ErrInfo)
            if not res:
                raise TradeError
            return res[0]
            
    def Repay(self, amount):
        assert self.isLogon()
        res = ResultBuffer()
        self._dll.Repay(self._clientId, amount, res.Result, res.ErrInfo)
        return res

if __name__ == "__main__":
    api = TradeApi.Instance()
    #f = open('out.txt', 'w+')
    #import sys
    #sys.stdout=f
    if not api.isLogon():
        api.Logon("59.173.7.38", 7708, "184039030", "326326")
    try:
        print type(api.QueryData(5))
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
        
        #rst = api.SendOrder(3, "000655", 20.22, 100)
        #print rst
        #print api.SendOrders([3,3,3], ["000655", "000625","600005"], [20.22, 10.11,6.4], [100,100,200])
        #print api.Buy("000690", 18.8, 100)
        #print api.Sell("000690", 10.10, 100)
        #print api.Short("600005", 6.4, 100)
    except ErrorExp as e:
        print "!!!!!!!!!!!!!!!!!!!!!"
        print type(e),e
    finally:
        print "Log off"
        api.Logoff()

    #f.close()
