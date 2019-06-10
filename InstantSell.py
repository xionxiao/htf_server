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

    # 取消订单
    c,d,e = sp.acquire(_stock, _share)
    if not c:
        return u"证券数量不足"
    rst = api.CancelOrder(c)
    if rst:
        for i in c:
            sp.removeOrder(i)
    else:
        return u"撤消订单失败"

##    if e != 0:
##        time.sleep(0.3)
##        rst = sp.fill(_stock, e)
##        if not rst:
##            ret_val += u"股票池拆单抢回失败"

    time.sleep(0.3)
    for try_times in range(3):
        # 获取即时价格
        _price = getProperPrice(_stock)
        # 下单
        ret_val += u" 价格 " + str(_price) + u" "
        if e == 0:
            rst = api.Short(_stock, _price, _share)
            # 若下单失败，重新用涨停价抢单
            if not rst:
                time.sleep(0.3)
                ret_val += u" 下单失败，抢回 "
                rst = sp.fill(_stock, _share)
                if rst:
                    ret_val += str(_share)
                else:
                    ret_val += u"失败"
                return ret_val
        else:
            rst = api.SendOrders([3,3],[_stock,_stock],[_price,_raising_price],[_share,e])
            # 若下单失败，重新用涨停价抢单
            if not rst:
                time.sleep(0.3)
                ret_val += u"2 下单失败，抢回 "
                refill_shares = 0
                if not rst[0]: # 订单失败
                    refill_shares += _share
                if not rst[1]: # 拆单后抢回失败
                    refile_shares += e
                rst = sp.fill(_stock, refill_shares)
                if rst:
                    ret_val += str(e)
                else:
                    ret_val += u"失败"
                return ret_val

        order_id = rst[0][0][0]
        e = 0 # 已经抢回，不需要重复抢单

        # 查询委托单是否为废单，若是废单抢回
        time.sleep(0.5)
        status = checkOrderStatus(order_id)
        if status == "废单":
            continue
        if status == "已报":
            api.CancelOrder(order_id)
            continue
        if status == "已成":
            ret_val += u"成功 " + str(order_id)
            break

    return ret_val

def checkOrderStatus(order_id, count = 3, check_interval=0.1):
    for i in range(count):
        rst = api.Query("当日委托")
        if rst and order_id in rst[0]["委托编号"]:
            index = rst[0]["委托编号"].index(order_id)
            status = rst[0]["状态说明"][index]
            return status
        time.sleep(check_interval)

def getProperPrice(stock):
    # 获取最合适价格
    lv2 = Lv2Api()
    rst = lv2.GetQuotes5(stock)
    if not rst:
        return u"获取行情失败"
    # 现价
    instant_price = round_up_decimal_2(float(rst[0][0][3]))
    bid_1 = round_up_decimal_2(float(rst[0][0][18]))
    buy_1 = round_up_decimal_2(float(rst[0][0][17]))
    print u"现价",instant_price
    print u"卖一价",bid_1
    print u"买一价", buy_1
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
    
