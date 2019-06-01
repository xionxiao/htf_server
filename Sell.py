# -*- coding: gbk -*-

from TradeApi import *
from Utils import *
from StockPool import *
from Cache import *
import time

def Sell(stock, price, share):
    api = TradeApi()
    if not api.isLogon():
        api.Open()
        rst = api.Logon("125.39.80.105", 443, "184039030", "326326")
        if not rst:
            return u"��¼ʧ��"
    
    _stock = stock.encode()
    _price = float(price)
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
        printd(rst)
        return u"��������ʧ��"
    
    time.sleep(0.5)
    if e == 0:
        rst = api.Short(_stock, _price, _share)
    else:
        rst = api.SendOrders([3,3],[_stock,_stock],[_price,_raising_price],[_share,e])

    printd(rst)
    # ���µ�ʧ�ܣ���������ͣ������
    if not rst:
        return u"ʧ��"

    return u"�ɹ�"

if __name__ == "__main__":
    print Sell("600", 37.53, 400)
    
