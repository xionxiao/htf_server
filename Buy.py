# -*- coding: gbk -*-

from TradeApi import *

def Buy(stock, price, share):
    api = TradeApi()
    api.Open()
    if api.Logon("59.173.7.38", 7708, "184039030", "326326"):
        rst = api.Buy(stock, float(price), int(share))
        print rst
    api.Logoff()
    api.Close()
    return rst

if __name__ == "__main__":
    Buy("000002", 13.00, 100)
