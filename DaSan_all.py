# -*- coding: gbk -*-

from TradeApi import *
from Utils import *
import time

def dasan_all():
    api = TradeApi()
    if not api.isLogon():
        rst = api.Logon("125.39.80.105", 443, "184039030", "326326")
        if not rst:
            return u"连接服务器失败"
    ret_val = ""

    # 在可撤单上筛选当前股票在涨停价格的卖单股数
    short_orders = []
    rst = api.Query("可撤单")
    if not rst:
        return u"查询可撤单失败"
    
    for i in rst:
        if i[13] == "融券卖出":
            short_orders.append(i)

    zqdm_list = list(set([i[1] for i in short_orders]))
    if not zqdm_list:
        return u"没有融券卖出单"
    
    quotes = api.GetQuote(zqdm_list)
    if not quotes:
        return u"查询行情失败"
    
    closing_price = [ float(q[1][2]) for q in quotes['result'] ]
    raising_price = [ round_up_decimal_2(c * 1.1) for c in closing_price ]
    print u"融券卖出订单"
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
    print u"需要打散的订单"
    print order_codes
    print order_ids
    print order_raising_price
    print order_shares
    
    print "----------------"
    for i in range(len(order_ids)):
        print u"取消订单" + str(order_ids[i])
        rst = api.CancelOrder(order_ids[i])
        if not rst:
            print u"取消失败"
            print rst
            continue
        time.sleep(0.5)
        print u"抢单 " + order_codes[i] + " " + str(order_raising_price[i])
        success = 0
        for n in range(order_shares[i]/100):
            time.sleep(0.2)
            rst = api.Short(order_codes[i], order_raising_price[i], 100)
            if not rst:
                print u"失败"
                print rst
                continue
            success += 100
            print "success : " + str(success)

    return ret_val

if __name__ == "__main__":
    # 委托号， 股票代码， 涨停价， 股数
    print dasan_all()
    
