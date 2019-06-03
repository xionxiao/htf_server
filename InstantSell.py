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
    c,d,e = sp.acquire(_stock, _share)
    if not c:
        return u"֤ȯ��������"
    rst = api.CancelOrder(c)
    if rst:
        for i in c:
            sp.removeOrder(i)
    else:
        return u"��������ʧ��"
    
    time.sleep(0.5)
    # ��ȡ��ʱ�۸�
    rst = api.Query("����",stock=_stock)
    if not rst:
        return u"��ȡ����ʧ��"

    instant_price = round_up_decimal_2(float(rst[0][0][5]))
    _price = instant_price
    print _price
    
    if e == 0:
        rst = api.Short(_stock, _price, _share)
        # ���µ�ʧ�ܣ���������ͣ������
        if not rst:
            api.Short(_stock, _raising_price, _share)
            return u"ʧ��"
    else:
        rst = api.SendOrders([3,3],[_stock,_stock],[_price,_raising_price],[_share,e])
        # ���µ�ʧ�ܣ���������ͣ������
        if not rst:
            if not rst[0]:
                api.Short(_stock, _raising_price, _share)
            if not rst[1]:
                api.Short(_stock, _raising_price, e)
            return u"ʧ��"

    order_id = rst[0][0][0]

    time.sleep(0.5)
    rst = api.Query("����ί��")
    if rst:
        if order_id in rst[0]["ί�б��"]:
            index = rst[0]["ί�б��"].index(order_id)
            status = rst[0]["״̬˵��"][index]
            if status == "�ϵ�":
                rst = api.Short(_stock, _price, _share)
                if rst:
                    return u"�ϵ� " + order_id + u" �����µ����ɹ�"
                else:
                    rst = api.Short(_stock, _raising_price, _share)
                    if rst:
                        return u"�ϵ� " + order_id + u" �����µ���ʧ��; ���� " + str(_share)
                    else:
                        return u"�ϵ� " + order_id + u" �����µ���ʧ��; ����ʧ��"

    return u"�ɹ�"

if __name__ == "__main__":
    print InstantSell("002294", 200)
    
