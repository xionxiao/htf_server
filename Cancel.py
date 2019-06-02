# -*- coding: gbk -*-

from TradeApi import *
from Utils import *
from Cache import *
import time

def Cancel(order_id):
    api = TradeApi()
    if not api.isLogon():
        api.Open()
        api.Logon("59.173.7.38", 7708, "184039030", "326326")
    cache = Cache()
    rst = api.Query("可撤单")
    order = None
    ret_val = ""
    if not rst:
        return u"查询可撤订单失败"
    # 解析rst, 找到对应的order的行
    if order_id in rst[0]["委托编号"]:
        index = rst[0]["委托编号"].index(order_id)
        order = rst[0][index]
    else:
        return u"没有此订单" + str(order_id)

    flag = order[4]
    # 判断买入卖出
    if flag == "买入":
        rst = api.CancelOrder(order_id)
        if not bool(rst):
            return u"撤单失败：\n"
        else:
            return u"撤单成功：\n"
    elif flag == "卖出":
        rst = api.CancelOrder(order_id)
        # 如果撤单成功
        if bool(rst):
            time.sleep(0.3)
            # 获得当前涨停价
            price = cache.get(order[1],"涨停价")
            # 涨停价下单
            rst = api.Short(order[1], price, int(float(order[8])))
            if rst:
                ret_val = u"撤单成功，抢回 " + order[8]
            else:
                ret_val = u"撤单成功, 抢回失败 " + str(rst)
        else:
            ret_val = u"撤单失败：\n" + str(rst).decode('string_escape')

    return ret_val

if __name__ == "__main__":
    print Cancel("196")
    
