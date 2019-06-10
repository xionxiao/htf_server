# -*- coding: gbk -*-

from TradeApi import *
from Utils import *
from StockPool import *
from Cache import *
import time

def InstantSell(stock, share):
    api = TradeApi()
    if not api.isLogon():
        rst = api.Logon("125.39.80.105", 443, "184039030", "326326")
        if not rst:
            return u"���ӷ�����ʧ��"

    _stock = stock.encode()
    _share = int(share)
    
    ret_val = ""
    sp = StockPool(api)
    cache = Cache(api)
    _raising_price = cache.get(_stock, "��ͣ��")

    # ȡ������
    c,d,e = sp.acquire(_stock, _share)
    if not c:
        return u"֤ȯ��������"
    rst = api.CancelOrder(c)
    if rst:
        for i in c:
            sp.removeOrder(i)
    else:
        return u"��������ʧ��"

##    if e != 0:
##        time.sleep(0.3)
##        rst = sp.fill(_stock, e)
##        if not rst:
##            ret_val += u"��Ʊ�ز�����ʧ��"

    time.sleep(0.3)
    for try_times in range(3):
        # ��ȡ��ʱ�۸�
        _price = getProperPrice(_stock)
        # �µ�
        ret_val += u" �۸� " + str(_price) + u" "
        if e == 0:
            rst = api.Short(_stock, _price, _share)
            # ���µ�ʧ�ܣ���������ͣ������
            if not rst:
                time.sleep(0.3)
                ret_val += u" �µ�ʧ�ܣ����� "
                rst = sp.fill(_stock, _share)
                if rst:
                    ret_val += str(_share)
                else:
                    ret_val += u"ʧ��"
                return ret_val
        else:
            rst = api.SendOrders([3,3],[_stock,_stock],[_price,_raising_price],[_share,e])
            # ���µ�ʧ�ܣ���������ͣ������
            if not rst:
                time.sleep(0.3)
                ret_val += u"2 �µ�ʧ�ܣ����� "
                refill_shares = 0
                if not rst[0]: # ����ʧ��
                    refill_shares += _share
                if not rst[1]: # �𵥺�����ʧ��
                    refile_shares += e
                rst = sp.fill(_stock, refill_shares)
                if rst:
                    ret_val += str(e)
                else:
                    ret_val += u"ʧ��"
                return ret_val

        order_id = rst[0][0][0]
        e = 0 # �Ѿ����أ�����Ҫ�ظ�����

        # ��ѯί�е��Ƿ�Ϊ�ϵ������Ƿϵ�����
        time.sleep(0.5)
        status = checkOrderStatus(order_id)
        if status == "�ϵ�":
            continue
        if status == "�ѱ�":
            api.CancelOrder(order_id)
            continue
        if status == "�ѳ�":
            ret_val += u"�ɹ� " + str(order_id)
            break

    return ret_val

def checkOrderStatus(order_id, count = 3, check_interval=0.1):
    for i in range(count):
        rst = api.Query("����ί��")
        if rst and order_id in rst[0]["ί�б��"]:
            index = rst[0]["ί�б��"].index(order_id)
            status = rst[0]["״̬˵��"][index]
            return status
        time.sleep(check_interval)

def getProperPrice(stock):
    # ��ȡ����ʼ۸�
    lv2 = Lv2Api()
    rst = lv2.GetQuotes5(stock)
    if not rst:
        return u"��ȡ����ʧ��"
    # �ּ�
    instant_price = round_up_decimal_2(float(rst[0][0][3]))
    bid_1 = round_up_decimal_2(float(rst[0][0][18]))
    buy_1 = round_up_decimal_2(float(rst[0][0][17]))
    print u"�ּ�",instant_price
    print u"��һ��",bid_1
    print u"��һ��", buy_1
    if instant_price > bid_1:
        price = bid_1
    else:
        price = instant_price
    return price

if __name__ == "__main__":
    api = TradeApi()
    if not api.isLogon():
        rst = api.Logon("125.39.80.105", 443, "184039030", "326326")
    
    sp = StockPool(api)
    cache = Cache(api)
    sp.sync()
    for i in range(5):
        print InstantSell("600875", 100)
        sp.sync()
        time.sleep(5)
    
