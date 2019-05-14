#!/usr/bin/python2
# coding gbk
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
                return [self._makeTable(self.Result.value)]
            else:
                return [self._makeTable(i) for i in self.Result]
        err = ["ErrInfo", "errInfo", "error", "Error"]
        if name in err:
            if type(self.ErrInfo) is c_char_p:
                return [self.ErrInfo.value]
            else:
                return [i for i in self.ErrInfo]
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
    # ��ѯ����
    QUERY_TYPE = ("�ʽ�",  # 0
                  "�ɷ�",  # 1 
                  "����ί��",  # 2
                  "���ճɽ�",  # 3
                  "�ɳ���",  # 4
                  "�ɶ�����",  # 5
                  "�������",  # 6
                  "��ȯ���",  # 7
                  "����֤ȯ"   # 8
                  )
    # ��������
    ORDER_TYPE = ("����", # 0
                  "����", # 1
                  "��������", # 2
                  "��ȯ����", # 3
                  "��ȯ��ȯ", # 4
                  "��ȯ����", # 5
                  "��ȯ��ȯ", # 6
                  )
    # ��ʷί������
    HISTORY_QUERY_TYPE = ("��ʷί��", # 0
                          "��ʷ�ɽ�", # 1
                          "���", # 2
                          )
    # �ɶ�����
    GDDM_TYPE = {'����':'0603467002',   # ����
                 '����':'E035674151'    # ����
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
        """ ������Ϣ��
                  "�ʽ�"       0
                  "�ɷ�"       1
                  "����ί��"    2
                  "���ճɽ�"    3
                  "�ɳ���"     4
                  "�ɶ�����"    5
                  "�������"    6
                  "��ȯ���"    7
                  "����֤ȯ"    8

           ��ʷί�У� ���� -- startTime=20150512, endTime=20150513
                  "��ʷί��"    11
                  "��ʷ�ɽ�"    12
                  "���"      13

           �嵵���飺  ���� -- zqdm="000002"
                  "����"     21
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
        elif u_str == "����":
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
                gddm = self.GDDM_TYPE['����']
            else:
                gddm = self.GDDM_TYPE['����']
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
                    gddm.append(self.GDDM_TYPE['����'])
                else:
                    gddm.append(self.GDDM_TYPE['����'])
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
    rst = api.Query("�ʽ�")
    print rst
    print str(rst[0]).decode("string_escape")
    print rst[0][3]
    print rst[0][3] == "�����ʽ�"
    #print Ex(api.Query("�ɷ�")[0])
    #print api.Query("����ί��")
    #print Ex(api.Query("���ճɽ�")[0])
    #print str(api.Query("�ɳ���")[0]).decode("string_escape")
    #print Ex(api.Query("�ɶ�����")[0])
    #print Ex(api.Query("�������")[0])
    #print api.Query("��ȯ���") # ϵͳ�ݲ�֧�ָù���
    #print Ex(api.Query("����֤ȯ")[0])

    #rst = api.QueryHistoryData(0, "20150429", "20150504")
    #print rst
    #print Ex(api.Query("��ʷί��", "20150429", "20150504")[0])
    #print Ex(api.Query("��ʷ�ɽ�", "20150429", "20150504")[0])
    #print Ex(api.Query("���", startDate="20150429", endDate="20150504")[0])

    #print Ex(api.GetQuote("000002")[0])
    #print api.Query("����", zqdm="000002")

    #print api.Repay("1000")
    #rst = api.CancelOrder(["1799","1798"])
    #print rst
    
    #print api.SendOrder(3, "000655", 20.22, 100)
    #print api.SendOrders([3,3,3], ["000655", "000625","600005"], [20.22, 10.11,6.4], [100,100,200])
    #print api.Buy("000690", 18.8, 100)
    #print api.Sell("000690", 10.10, 100)
    #print api.Short("600005", 6.4, 100)

    #f.close()
    api.Logoff()
    api.Close()
