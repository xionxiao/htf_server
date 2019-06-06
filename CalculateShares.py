# -*- coding: gbk -*-

from TradeApi import *
from Utils import *
import time

def calcShares():
    api = TradeApi()
    if not api.isLogon():
        rst = api.Logon("180.166.192.130", 7708, "184039030", "326326")
        if not rst:
            return u"连接服务器失败"

    # 在可撤单上筛选融券卖出
    order = None
    rst = api.Query("可撤单")
    if not rst:
        print rst
        return

    orders = []
    for i in rst:
        if i[13] == "融券卖出":
            orders.append(i)

    # 取得每只股票的代码
    stocks = list(set([ i[1] for i in orders ]))
    #print stocks
    if not stocks:
        return u"股票池为空"

    # 转换为字典，value[0] -- 涨停价; value[1] -- 股数
    sdict = dict((i, [-1,0,""]) for i in stocks)
    # 计算涨停价
    rst = api.GetQuote(stocks)
    if not rst:
        return
    for i in rst['result']:
        rlimit = round_up_decimal_2(float(i[1][2]) * 1.1)
        sdict[i[1][0]][0] = rlimit
        sdict[i[1][0]][2] = i[1][1]

    # 累加股数
    for i in orders:
        if sdict[i[1]][0] == round_up_decimal_2(float(i[7])):
            sdict[i[1]][1] += int(float(i[8]))

    i = 1
    for k,v in sdict.iteritems():
        print i,k,v[2],v[1],v[0]
        i += 1

    return ""

if __name__ == "__main__":
    # 委托号， 股票代码， 涨停价， 股数
    print calcShares()
