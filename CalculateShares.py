# -*- coding: gbk -*-

from TradeApi import *
from Utils import *
import time

def calcShares():
    api = TradeApi()
    if not api.isLogon():
        rst = api.Logon("180.166.192.130", 7708, "184039030", "326326")
        if not rst:
            return u"���ӷ�����ʧ��"

    # �ڿɳ�����ɸѡ��ȯ����
    order = None
    rst = api.Query("�ɳ���")
    if not rst:
        print rst
        return

    orders = []
    for i in rst:
        if i[13] == "��ȯ����":
            orders.append(i)

    # ȡ��ÿֻ��Ʊ�Ĵ���
    stocks = list(set([ i[1] for i in orders ]))
    #print stocks
    if not stocks:
        return u"��Ʊ��Ϊ��"

    # ת��Ϊ�ֵ䣬value[0] -- ��ͣ��; value[1] -- ����
    sdict = dict((i, [-1,0,""]) for i in stocks)
    # ������ͣ��
    rst = api.GetQuote(stocks)
    if not rst:
        return
    for i in rst['result']:
        rlimit = round_up_decimal_2(float(i[1][2]) * 1.1)
        sdict[i[1][0]][0] = rlimit
        sdict[i[1][0]][2] = i[1][1]

    # �ۼӹ���
    for i in orders:
        if sdict[i[1]][0] == round_up_decimal_2(float(i[7])):
            sdict[i[1]][1] += int(float(i[8]))

    i = 1
    for k,v in sdict.iteritems():
        print i,k,v[2],v[1],v[0]
        i += 1

    return ""

if __name__ == "__main__":
    # ί�кţ� ��Ʊ���룬 ��ͣ�ۣ� ����
    print calcShares()
