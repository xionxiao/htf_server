# -*- coding: gbk -*-

from TradeApi import *
from Utils import *

def Buy(stock, price, share):
    api = TradeApi()
    api.Open()
    retval = u""
    if api.Logon("59.173.7.38", 7708, "184039030", "326326"):
        rst = api.Buy(stock, float(price), int(share))
        printd(rst)
        if rst:
            retval = str(rst[0]["ί�б��"][0])
            print retval
        else:
            retval = str(rst[0]).decode("gbk")
        
    api.Logoff()
    api.Close()
    return retval

if __name__ == "__main__":
    Buy("000002", 13.00, 100)
