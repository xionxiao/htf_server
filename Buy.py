# -*- coding: gbk -*-

from TradeApi import *
from Utils import *

def Buy(stock, price, share):
    api = TradeApi()
    if not api.isLogon():
        api.Open()
        api.Logon("59.173.7.38", 7708, "184039030", "326326")
    retval = u""
    rst = api.Buy(stock, float(price), int(share))
    if rst:
        retval = str(rst[0]["委托编号"][0])
        print retval
    else:
        retval = str(rst[0]).decode("gbk")

    return retval

if __name__ == "__main__":
    Buy("000002", 13.00, 100)
