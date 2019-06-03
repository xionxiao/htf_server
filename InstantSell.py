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
            return u"连接服务器失败"
    
    _stock = stock.encode()
    _share = int(share)
    
    ret_val = ""
    sp = StockPool(api)
    cache = Cache(api)
    _raising_price = cache.get(_stock, "涨停价")
    c,d,e = sp.acquire(_stock, _share)
    if not c:
        return u"证券数量不足"
    rst = api.CancelOrder(c)
    if rst:
        for i in c:
            sp.removeOrder(i)
    else:
        return u"撤消订单失败"
    
    time.sleep(0.5)
    # 获取即时价格
    rst = api.Query("行情",stock=_stock)
    if not rst:
        return u"获取行情失败"

    instant_price = round_up_decimal_2(float(rst[0][0][5]))
    _price = instant_price
    print _price
    
    if e == 0:
        rst = api.Short(_stock, _price, _share)
        # 若下单失败，重新用涨停价抢单
        if not rst:
            api.Short(_stock, _raising_price, _share)
            return u"失败"
    else:
        rst = api.SendOrders([3,3],[_stock,_stock],[_price,_raising_price],[_share,e])
        # 若下单失败，重新用涨停价抢单
        if not rst:
            if not rst[0]:
                api.Short(_stock, _raising_price, _share)
            if not rst[1]:
                api.Short(_stock, _raising_price, e)
            return u"失败"

    order_id = rst[0][0][0]

    time.sleep(0.5)
    rst = api.Query("当日委托")
    if rst:
        if order_id in rst[0]["委托编号"]:
            index = rst[0]["委托编号"].index(order_id)
            status = rst[0]["状态说明"][index]
            if status == "废单":
                rst = api.Short(_stock, _price, _share)
                if rst:
                    return u"废单 " + order_id + u" 重新下单，成功"
                else:
                    rst = api.Short(_stock, _raising_price, _share)
                    if rst:
                        return u"废单 " + order_id + u" 重新下单，失败; 抢回 " + str(_share)
                    else:
                        return u"废单 " + order_id + u" 重新下单，失败; 抢回失败"

    return u"成功"

if __name__ == "__main__":
    print InstantSell("002294", 200)
    
