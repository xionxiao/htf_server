# -*- coding: gbk -*-

from ctypes import *
from Utils import *
from ResultBuffer import *
import datetime
import time

class Error(Exception):
    pass

class LogonError(Error):
    u""" ��¼���� """
    pass

class QueryError(Error):
    u""" ��ѯ���� """
    def __init__(self, query_type, error_info, *args, **kwargs):
        # TODO: ����History Query
        self._query_type = query_type
        self._error_info = error_info

    def __str__(self):
        ret_val = "��ѯ" + self._query_type + "ʧ��: " + self._error_info
        return ret_val

class TradeError(Error):
    u""" ���״��� """
    def __init__(self, orderType, stock, price, quantitiy, priceType):
        pass

@Singleton
class TradeApi():
    __clientId = -1
    __ip = ""
    __port = None
    
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
    # �ɶ����� ����֤ȯ
    GDDM_CJZQ = { '����':'0603467002', '����':'E035674151' }
    
    # �ɶ����� ��̩����
    GDDM_GTJA = { '����':'0603710116', '����':'E037015793' }

    GDDM_TYPE = GDDM_CJZQ
    
    def __init__(self):
        """ When load fails this may throw WindowsError exception """
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

    def GetEdition(self):
        rst = ResultBuffer()
        self._dll.GetEdition(rst.Result)
        return rst
    
    def Logon(self, ip, port, account, password, TxPassword="", version="9.01"):
        u""" ��¼������ """
        assert isValidIpAddress(ip), 'Not a valid IP address'
        assert type(port) is int, 'Port must be int'
        assert type(account) is str
        assert type(password) is str
        
        rst = ResultBuffer()
        client = self._dll.Logon(ip, port, version, account, password, TxPassword, rst.ErrInfo)
        if client == -1:
            raise LogonError,"Logon failed: " + rst.ErrInfo.value
        self.__clientId = client
        self.__ip = ip
        self.__port = port

    def Logoff(self):
        if self.__clientId != -1:
            self._dll.Logoff(self.__clientId)
            self.__clientId = -1

    def isLogon(self):
        u""" ����Ƿ��ѵ�¼ """
        # ��� clientId ʧЧ���ڵ�������APIʱ���׳�WindowsError�쳣�� Error -1073741816
        return bool(self.__clientId != -1)
    
    def QueryData(self, category):
        u""" ��ѯ���ֽ�������
             0�ʽ�  1�ɷ�   2����ί��  3���ճɽ�    4�ɳ���   5�ɶ�����  6�������   7��ȯ���  8����֤ȯ
        """
        assert self.__clientId != -1, "Does not logon, need logon first!"
        assert type(category) is int
        assert category in range(len(self.QUERY_TYPE))
        
        res = ResultBuffer()
        self._dll.QueryData(self.__clientId, category, res.Result, res.ErrInfo)
        if not res:
            # Todo: ���õ�QueryException���캯��
            raise QueryError(self.QUERY_TYPE(category), rst.ErrInfo.value)
        return res[0]

    def QueryDatas(self, categories):
        u""" ��ѯ���ֽ�������:
             categories is query type list.
             0�ʽ�  1�ɷ�   2����ί��  3���ճɽ�    4�ɳ���   5�ɶ�����  6�������   7��ȯ���  8����֤ȯ
        """
        assert self.__clientId != -1, "Does not logon, need logon first!"
        assert type(categories) is list
        assert len(categories) > 0
        
        count = len(categories)
        for cat in categories:
            assert cat in range(len(self.QUERY_TYPE))
        _category = c_array(category, c_int)
        res = ResultBuffer(count)
        self._dll.QueryDatass(self.__clientId, _category, count, res.Result, res.ErrInfo)
        if not res:
            # TODO: �������ĸ���ѯʧ��
            raise QueryError
        return res

    def QueryHistoryData(self, histQueryType, startDate, endDate):
        u""" ��ѯ��ʷ�������ݣ�
             0��ʷί��  1��ʷ�ɽ�   2���
             ���ڸ�ʽ: 20140301
        """
        assert(self.__clientId != -1)
        assert(category in range(len(self.HISTORY_QUERY_TYPE)))
        assert(isValidDate(startDate))
        assert(isValidDate(endDate))
        res = ResultBuffer()
        self._dll.QueryHistoryData(self.__clientId, histQueryType, startDate, endDate, res.Result, res.ErrInfo)
        if not res:
            # TODO: more information
            raise QueryError(self.HISTORY_QUERY_TYPE(histQueryType), rst.ErrInfo.value)
        return res

    def Query(self, u_str, *args, **kwargs):
        u""" ������Ϣ��
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

           �嵵���飺  ���� -- stock="000002"
                  "����"     21
                  "���ռ�"    22
                  "�񿪼�"    23
                  "��ǰ��"    24
                  "��ͣ��"    25
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
            elif len(args) == 0 and kwargs['stock']:
                return self.GetQuote(kwargs['stock'])
        elif u_str == "���ռ�":
            if len(args) == 1:
                rst = self.GetQuote(args[0])
                return round_up_decimal_2(float(rst[0][2]))
            elif len(args) == 0 and kwargs['stock']:
                rst = self.GetQuote(kwargs['stock'])
                return [ round_up_decimal_2(float(i[0][2])) for i in rst ]
        elif u_str == "��ͣ��":
            if len(args) == 1:
                rst = self.GetQuote(args[0])
                return round_up_decimal_2(float(rst[0][2]*1.1))
            elif len(args) == 0 and kwargs['stock']:
                rst = self.GetQuote(kwargs['stock'])
                return [ round_up_decimal_2(float(i[0][2])*1.1) for i in rst ]
        elif u_str == "��ǰ��":
            if len(args) == 1:
                rst = self.GetQuote(args[0])
                return round_up_decimal_2(float(rst[0][5]))
            elif len(args) == 0 and kwargs['stock']:
                rst = self.GetQuote(kwargs['stock'])
                return [ round_up_decimal_2(float(i[0][5])) for i in rst ]
        elif u_str == "�񿪼�":
            if len(args) == 1:
                rst = self.GetQuote(args[0])
                return round_up_decimal_2(float(rst[0][3]))
            elif len(args) == 0 and kwargs['stock']:
                rst = self.GetQuote(kwargs['stock'])
                return [ round_up_decimal_2(float(i[0][3])) for i in rst ] 

    def SendOrder(self, orderType, zqdm, price, quantity, priceType=0, gddm=''):
        # 0�Ϻ��޼�ί�� �����޼�ί��
        # 1(�м�ί��)���ڶԷ����ż۸�
        # 2(�м�ί��)���ڱ������ż۸�
        # 3(�м�ί��)���ڼ�ʱ�ɽ�ʣ�೷��
        # 4(�м�ί��)�Ϻ��嵵����ʣ�� �����嵵����ʣ��
        # 5(�м�ί��)����ȫ��ɽ�����
        # 6(�м�ί��)�Ϻ��嵵����ת�޼�
        # TODO: �������
        if self.__clientId == -1:
            return
        res = ResultBuffer()
        if not gddm:
            if zqdm[0] == '6':
                gddm = self.GDDM_TYPE['����']
            else:
                gddm = self.GDDM_TYPE['����']
        self._dll.SendOrder(self.__clientId, orderType, priceType, gddm, zqdm, c_float(price), quantity, res.Result, res.ErrInfo)
        if not rst:
            # TODO: TradeException��ϸ��Ϣ
            raise TradeError
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
            # Fix Bug when only one command in banch
            if count == 1:
                return self.GetQuote(zqdm[0])
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
    api = TradeApi.Instance()
    rst = api.GetEdition()
    printd(rst)
    #f = open('out.txt', 'w+')
    #import sys
    #sys.stdout=f
    if not api.isLogon():
        api.Logon("59.173.7.38", 7708, "184039030", "326326")
    try:    
        print api.QueryData(0)
        rst = api.Query("�ʽ�")
        printd(rst)
        print rst.head[3] == "�����ʽ�"

        print u"======== �ɷ�"
        rst = api.Query("�ɷ�")
       
        printd(rst)
        print u"======== ����ί��"
        printd(api.Query("����ί��"))
        print u"======== ���ճɽ�"
        printd(api.Query("���ճɽ�"))
        print u"======== �ɳ���"
        printd(api.Query("�ɳ���"))
        print u"======== �ɶ�����"
        printd(api.Query("�ɶ�����"))
        print u"======== �������"
        printd(api.Query("�������"))
        #print u"======== ��ȯ���"
        #printd(api.Query("��ȯ���")) # ϵͳ�ݲ�֧�ָù���
        print u"======== ����֤ȯ"
        printd(api.Query("����֤ȯ").head)
        print "========"

        #rst = api.QueryHistoryData(0, "20150429", "20150504")
        #printd(rst)
        #printd(api.Query("��ʷί��", "20150429", "20150504")[0])
        #printd(api.Query("��ʷ�ɽ�", "20150429", "20150504")[0])
        #printd(api.Query("���", startDate="20150429", endDate="20150504")[0])

        rst = api.Query("��ǰ��", stock="000002")
        printd(rst)

        #print api.Repay("1000")
        #rst = api.CancelOrder(["1799","1798"])
        #print rst
        
        #print api.SendOrder(3, "000655", 20.22, 100)
        #print api.SendOrders([3,3,3], ["000655", "000625","600005"], [20.22, 10.11,6.4], [100,100,200])
        #print api.Buy("000690", 18.8, 100)
        #print api.Sell("000690", 10.10, 100)
        #print api.Short("600005", 6.4, 100)
    except Exception as e:
        print "!!!!!!!!!!!!!!!!!!!!!"
        print e
        raise "Error"
    finally:
        print "Log off"
        api.Logoff()

    #f.close()
