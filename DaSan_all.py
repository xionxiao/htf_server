# -*- coding: gbk -*-

from TradeApi import *
from Utils import *
import time

def dasan_all():
    api = TradeApi()
    if not api.isLogon():
        rst = api.Logon("125.39.80.105", 443, "184039030", "326326")
        if not rst:
            return u"���ӷ�����ʧ��"
    ret_val = ""

    # �ڿɳ�����ɸѡ��ǰ��Ʊ����ͣ�۸����������
    short_orders = []
    rst = api.Query("�ɳ���")
    if not rst:
        return u"��ѯ�ɳ���ʧ��"
    
    for i in rst:
        if i[13] == "��ȯ����":
            short_orders.append(i)

    zqdm_list = list(set([i[1] for i in short_orders]))
    if not zqdm_list:
        return u"û����ȯ������"
    
    quotes = api.GetQuote(zqdm_list)
    if not quotes:
        return u"��ѯ����ʧ��"
    
    closing_price = [ float(q[1][2]) for q in quotes['result'] ]
    raising_price = [ round_up_decimal_2(c * 1.1) for c in closing_price ]
    print u"��ȯ��������"
    print zqdm_list
    print raising_price

    order_codes = []
    order_ids = []
    order_shares = []
    order_raising_price = []
    for s in short_orders:
        i = zqdm_list.index(s[1])
        if float(s[7]) == raising_price[i] and int(float(s[8])) > 100:
            order_codes.append(s[1])
            order_ids.append(s[9])
            order_shares.append(int(float(s[8])))
            order_raising_price.append(raising_price[i])

    print "----------------"
    print u"��Ҫ��ɢ�Ķ���"
    print order_codes
    print order_ids
    print order_raising_price
    print order_shares
    
    print "----------------"
    for i in range(len(order_ids)):
        print u"ȡ������" + str(order_ids[i])
        rst = api.CancelOrder(order_ids[i])
        if not rst:
            print u"ȡ��ʧ��"
            print rst
            continue
        time.sleep(0.5)
        print u"���� " + order_codes[i] + " " + str(order_raising_price[i])
        success = 0
        for n in range(order_shares[i]/100):
            time.sleep(0.2)
            rst = api.Short(order_codes[i], order_raising_price[i], 100)
            if not rst:
                print u"ʧ��"
                print rst
                continue
            success += 100
            print "success : " + str(success)

    return ret_val

if __name__ == "__main__":
    # ί�кţ� ��Ʊ���룬 ��ͣ�ۣ� ����
    print dasan_all()
    
