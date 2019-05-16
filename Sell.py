# -*- coding: gbk -*-

from TradeApi import *
import time

def Sell(stock, price, share):
    api = TradeApi()
    api.Open()

    _stock = stock.encode()
    _price = float(price)
    _share = int(share)
    ret_val = ""
    if api.Logon("59.173.7.38", 7708, "184039030", "326326"):
        # 计算涨停价
        rst = api.GetQuote(_stock)
        raising_limit = round(float(rst[1][2]) * 1.1, 2)
        print raising_limit
        
        # 在可撤单上筛选当前股票在涨停价格的卖单股数
        orders = []
        rst = api.Query("可撤单")
        for i in rst:
            if i[1] == _stock and float(i[7]) == raising_limit and i[13] == "融券卖出":
                orders.append(i[9]) # 委托编号
        
        # 判断股票是否充足
        count = int(_share/100)
        if len(orders) < int(_share/100):
            return u"股票不足"
        
        # 若充足，选取相应股数单号
        print orders[0:count]

        # 撤单
        rst = api.CancelOrder(orders[0:count])
        if not bool(rst):
            print rst
            return u"撤单失败"
        
        # 延时0.3ms
        time.sleep(0.3)
        # 下单
        rst = api.Short(_stock, _price, _share)
        # 若下单失败，重新用涨停价抢单
        if not bool(rst):
            print rst
            ret_val = u"下单失败"
            back = 0
            for i in range(count):
                rst = api.Short(_stock, raising_limit, 100)
                time.sleep(0.2)
                if rst: back += 100
            ret_val += u'\n抢回 ' + str(back)
            return ret_val
        
        order_id = rst[1][0]
        time.sleep(0.5)
        # 检查是否为废单
        rst = api.Query("当日委托")
        for i in rst:
            if i[13] == order_id and i[6] == "废单":
                ret_val = u"废单"
                print u"废单"
                back = 0
                for i in range(count):
                    time.sleep(0.2)
                    print u"抢单"
                    rst = api.Short(_stock, raising_limit, 100)
                    if rst: back += 100
                ret_val += u'\n抢回 ' + str(back) 
        if not ret_val:
            ret_val = u"已报，单号：" + str(order_id)
        
        # 若抢单失败，则查询可用余额 (暂时不做)
        # 按最大可用余额重新抢单 (暂时不做)
        #print rst

    api.Logoff()
    api.Close()
    return ret_val

if __name__ == "__main__":
    print Sell("601669", 16.80, 300)
    
