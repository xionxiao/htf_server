# -*- coding: gbk -*-

from TradeApi import *
from Utils import *

class Commands(object):
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
        elif u_str == "昨收价":
            if len(args) == 1:
                rst = self.GetQuote(args[0])
                return round_up_decimal_2(float(rst[0][2]))
            elif len(args) == 0 and kwargs['stock']:
                rst = self.GetQuote(kwargs['stock'])
                return [ round_up_decimal_2(float(i[0][2])) for i in rst ]
        elif u_str == "涨停价":
            if len(args) == 1:
                rst = self.GetQuote(args[0])
                return round_up_decimal_2(float(rst[0][2]*1.1))
            elif len(args) == 0 and kwargs['stock']:
                rst = self.GetQuote(kwargs['stock'])
                return [ round_up_decimal_2(float(i[0][2])*1.1) for i in rst ]
        elif u_str == "当前价":
            if len(args) == 1:
                rst = self.GetQuote(args[0])
                return round_up_decimal_2(float(rst[0][5]))
            elif len(args) == 0 and kwargs['stock']:
                rst = self.GetQuote(kwargs['stock'])
                return [ round_up_decimal_2(float(i[0][5])) for i in rst ]
        elif u_str == "今开价":
            if len(args) == 1:
                rst = self.GetQuote(args[0])
                return round_up_decimal_2(float(rst[0][3]))
            elif len(args) == 0 and kwargs['stock']:
                rst = self.GetQuote(kwargs['stock'])
                return [ round_up_decimal_2(float(i[0][3])) for i in rst ] 

    def Buy(self, zqdm, price, share):
        return self.SendOrder(0, zqdm, price, share)

    def Sell(self, zqdm, price, share):
        return self.SendOrder(1, zqdm, price, share)

    def Short(self, zqdm, price, share):
        return self.SendOrder(3, zqdm, price, share)
