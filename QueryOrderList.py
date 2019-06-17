# -*- coding: gbk -*-

from TradeApi import *
from Utils import *
from StockPool import *
import json

def queryOrderList():
    api = TradeApi.Instance()
    if not api.isLogon():
        api.Logon("59.173.7.38", 7708, "184039030", "326326")

    sp = StockPool.Instance()
    sp_dict = sp.getStocks()
    order_list = {}
    rst = api.Query("当日成交")
    if not rst:
        return u"查询当日委托失败"
    for o in rst[0]:
        if len(o) == 0:
            break
        item = {"证券代码": o[1],
                "证券名称": o[2],
                "买卖标志": o[4],
                "成交价格": o[6],
                "成交数量": o[7],
                "成交时间": o[0]
                }
        order_list[o[9]] = item
    json_dumps = json.dumps(order_list, encoding="gbk").decode("utf8")
    return json_dumps


if __name__ == "__main__":
    api = TradeApi.Instance()
    if not api.isLogon():
        api.Logon("59.173.7.38", 7708, "184039030", "326326")
    sp = StockPool.Instance()
    sp.sync()
    queryOrderList()
