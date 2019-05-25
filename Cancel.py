# -*- coding: gbk -*-

from TradeApi import *
from Utils import *
import time

def Cancel(order_id):
    api = TradeApi()
    api.Open()
    api.Logon("59.173.7.38", 7708, "184039030", "326326")
    rst = api.Query("可撤单")
    order = None
    ret_val = ""
    # 解析rst, 找到对应的order的行
    for i in rst:
        if i[9] == order_id:
            order = i
            break

    # 没找到返回
    if not order:
        return u"没有该订单:" + str(order_id)

    flag = order[4]
    # 判断买入卖出
    if flag == "买入":
        rst = api.CancelOrder(order_id)
        if not bool(rst):
            return u"撤单失败：\n" + str(rst).decode('string_escape')
        else:
            return u"撤单成功：\n" + str(rst).decode('string_escape')
    elif flag == "卖出":
        rst = api.CancelOrder(order_id)
        print bool(rst)
        # 如果撤单成功
        if bool(rst):
            time.sleep(0.3)
            # 获得当前涨停价
            print order[1]
            rst = api.Query("行情", str(order[1]))
            price = round_up_decimal_2(float(rst[1][2]) * 1.1)
            print price
            back_amount = 0
            # 涨停价下单
            for x in range(int(float(order[8]))/100):
                time.sleep(0.2)
                rst = api.Short(i[1], price, 100)
                back_amount += 100
            ret_val = u"撤单成功,抢回 " + str(back_amount)
        else:
            ret_val = u"撤单失败：\n" + str(rst).decode('string_escape')

    api.Logoff()
    api.Close()
    return ret_val

if __name__ == "__main__":
    print Cancel("3890")
    
