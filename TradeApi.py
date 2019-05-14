#!/usr/bin/python2
#coding utf-8
from ctypes import *
import datetime
import time

def c_array(src_list, TYPE):
    if type(src_list) is not list: return
    count = len(src_list)
    rst = (TYPE*count)()
    for i in range(count): rst[i] = TYPE(src_list[i])
    return rst

class ResultBuffer(object):
    def __init__(self, count=1):
        if count == 1:
            self.ErrInfo = c_char_p('\000'*256)
            self.Result = c_char_p('\000'*1024*1024)
            self.count = 1
        elif count > 1:
            self.ErrInfo = (c_char_p*count)()
            self.Result = (c_char_p*count)()
            self.count = count
            for i in range(count):
                self.ErrInfo[i] = c_char_p('\000'*256)
                self.Result[i] = c_char_p('\000'*1024*1024)

    def __len__(self):
        return self.count

    def _makeTable(self, tab_str):
        rows = tab_str.split('\n')
        tab = [ r.split('\t') for r in rows ]
        return tab
        
    def __getitem__(self, name):
        rst = ["Result", "result"]
        if name in rst:
            if type(self.Result) is c_char_p:
                return [self._makeTable(self.Result.value.decode('gbk').encode('utf-8'))]
            else:
                return [self._makeTable(i.decode('gbk').encode('utf-8')) for i in self.Result]
        err = ["ErrInfo", "errInfo", "error", "Error"]
        if name in err:
            if type(self.ErrInfo) is c_char_p:
                return [self.ErrInfo.value]
            else:
                return [i.decode('gbk').encode('utf-8') for i in self.ErrInfo]
        if type(name) is int:
            if not bool(self):
                return self["Error"][name]
            else:
                if type(self.Result) is list:
                    return self['Result'][name]
                else:
                    return self['Result'][0][name]

    def __nonzero__(self):
        if type(self.ErrInfo) is c_char_p:
            return self.ErrInfo.value == ""
        else:
            err = [ not bool(i) for i in self.ErrInfo]
            return bool(sum(err))

    def __str__(self):
        if bool(self):
            ss = ""
            for i in self['Result']:
                for j in i:
                    ss += str(j).decode('string_escape')+'\n'
            return ss
        else:
            return str(self['Error']).decode('string_escape')


class TradeApi(object):
    __clientId = -1
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
    # 股东代码
    GDDM_TYPE = {'深市':'0603467002',   # 深市
                 '沪市':'E035674151'    # 沪市
                 }
    
    def __init__(self):
        self._dll = windll.LoadLibrary("trade.dll")
        
    def Open(self):
        self._dll.OpenTdx()

    def Close(self):
        self._dll.CloseTdx()

    def GetEdition(self):
        rst = ResultBuffer()
        self._dll.GetEdition(rst.Result)
        return rst['Result']
    
    def Logon(self, ip, port, account, password, version="9.01"):
        TxPassword = ""
        rst = ResultBuffer()
        client = self._dll.Logon(ip, port, version, account, password, TxPassword, rst.ErrInfo)
        if client != -1:
            self.__clientId = client
        return rst

    def Logoff(self):
        if self.__clientId != -1:
            self._dll.Logoff(self.__clientId)


    def QueryData(self, category):
        if self.__clientId == -1:
            return
        if type(category) is list:
            count = len(category)
            _category = c_array(category, c_int)
            res = ResultBuffer(count)
            self._dll.QueryDatass(self.__clientId, _category, count, res.Result, res.ErrInfo)
            return res
        else:
            res = ResultBuffer()
            self._dll.QueryData(self.__clientId, category, res.Result, res.ErrInfo)
            return res
    
    def QueryHistoryData(self, histQueryType, startDate, endDate):
        if self.__clientId == -1:
            return
        res = ResultBuffer()
        self._dll.QueryHistoryData(self.__clientId, histQueryType, startDate, endDate, res.Result, res.ErrInfo)
        return res

    def Query(self, u_str, *args, **kwargs):
        """ 交易信息：
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

           五档行情：  参数 -- zqdm="000002"
                  "行情"     21
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
            elif len(args) == 0 and kwargs['zqdm']:
                return self.GetQuote(kwargs['zqdm'])

    def SendOrder(self, orderType, zqdm, price, quantity, priceType=0, gddm=''):
        if self.__clientId == -1:
            return
        res = ResultBuffer()
        if not gddm:
            if zqdm[0] == '6':
                gddm = self.GDDM_TYPE['沪市']
            else:
                gddm = self.GDDM_TYPE['深市']
        self._dll.SendOrder(self.__clientId, orderType, priceType, gddm, zqdm, c_float(price), quantity, res.Result, res.ErrInfo)
        return res

    def SendOrders(self, orderType, zqdm, price, quantity, priceType=0, gddm=[]):
        count = len(orderType)
        if len(zqdm)!=count or len(price)!=count or len(quantity)!=count:
            return
        # Bug when only one command in banch
        if count == 1:
            return self.SendOrder(orderType[0], zqdm[0], price[0], quantity[0], 0, gddm)
        
        res = ResultBuffer(count)
        _orderType = c_array(orderType, c_int)
        _zqdm = c_array(zqdm, c_char_p)
        _price = c_array(price, c_float)
        _quantity = c_array(quantity, c_int)
        _priceType = c_array([priceType]*count, c_int)
        if not gddm:
            gddm = []
            for i in zqdm:
                if i[0] == '6':
                    gddm.append(self.GDDM_TYPE['沪市'])
                else:
                    gddm.append(self.GDDM_TYPE['深市'])
        _gddm = c_array(gddm, c_char_p)

        self._dll.SendOrders(self.__clientId, _orderType, _priceType, _gddm, _zqdm, _price, _quantity, count, res.Result, res.ErrInfo)
        return res

    def Buy(self, zqdm, price, share):
        return self.SendOrder(0, zqdm, price, share)

    def Sell(self, zqdm, price, share):
        return self.SendOrder(1, zqdm, price, share)

    def Short(self, zqdm, price, share):
        return self.SendOrder(3, zqdm, price, share)
    
    def CancelOrder(self, orderId):
        if self.__clientId == -1:
            return
        if type(orderId) is list:
            count = len(orderId)
            # Fix Bug when only one command in banch
            if count == 1:
                return self.CancelOrder(orderId[0])
            res = ResultBuffer(count)
            _orderId = c_array(orderId, c_char_p)
            self._dll.CancelOrders(self.__clientId, _orderId, count, res.Result, res.ErrInfo)
            return res
        else:
            res = ResultBuffer()
            self._dll.CancelOrder(self.__clientId, orderId, res.Result, res.ErrInfo)
            return res

    def GetQuote(self, zqdm):
        if self.__clientId == -1:
            return
        if type(zqdm) is list:
            count = len(zqdm)
            _zqdm = c_array(zqdm, c_char_p)
            res = ResultBuffer(count)
            self._dll.GetQuotes(self.__clientId, _zqdm, count, res.Result, res.ErrInfo)
            return res
        else:
            res = ResultBuffer()
            self._dll.GetQuote(self.__clientId, zqdm, res.Result, res.ErrInfo)
            return res
            
    def Repay(self, amount):
        if self.__clientId == -1:
            return
        res = ResultBuffer()
        self._dll.Repay(self.__clientId, amount, res.Result, res.ErrInfo)
        return res

if __name__ == "__main__":
    def Ex(ss):
        return str(ss).decode("string_escape")
    
    api = TradeApi()
    #print api.GetEdition()
    #f = open('out.txt', 'w+')
    #import sys
    #sys.stdout=f
    api.Open()
    rst = api.Logon("119.147.80.108", 443, "184039030", "326326")
    #print api.QueryData(0)
    #rst = api.Query("资金")
    #print rst
    #print str(rst[0]).decode("string_escape")
    #print rst[0][3].decode('utf-8')
    #print rst[0][3] == "冻结资金"
    #print Ex(api.Query("股份")[0])
    #print api.Query("当日委托")
    #print Ex(api.Query("当日成交")[0])
    #print str(api.Query("可撤单")[0]).decode("string_escape")
    #print Ex(api.Query("股东代码")[0])
    #print Ex(api.Query("融资余额")[0])
    #print api.Query("融券余额") # 系统暂不支持该功能
    #print Ex(api.Query("可融证券")[0])

    #rst = api.QueryHistoryData(0, "20150429", "20150504")
    #print rst
    #print Ex(api.Query("历史委托", "20150429", "20150504")[0])
    #print Ex(api.Query("历史成交", "20150429", "20150504")[0])
    #print Ex(api.Query("交割单", startDate="20150429", endDate="20150504")[0])

    #print Ex(api.GetQuote("000002")[0])
    #print api.Query("行情", zqdm="000002")

    #print api.Repay("1000")
    #rst = api.CancelOrder(["1799","1798"])
    #print rst
    
    #print api.SendOrder(3, "000655", 20.22, 100)
    #print api.SendOrders([3,3,3], ["000655", "000625","600005"], [20.22, 10.11,6.4], [100,100,200])
    print api.Buy("000690", 18.8, 100)
    print api.Sell("000690", 10.10, 100)
    print api.Short("600005", 6.4, 100)

    #f.close()
    api.Logoff()
    api.Close()
