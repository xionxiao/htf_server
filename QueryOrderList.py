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
    rst = api.Query("���ճɽ�")
    if not rst:
        return u"��ѯ����ί��ʧ��"
    for o in rst[0]:
        if len(o) == 0:
            break
        item = {"֤ȯ����": o[1],
                "֤ȯ����": o[2],
                "������־": o[4],
                "�ɽ��۸�": o[6],
                "�ɽ�����": o[7],
                "�ɽ�ʱ��": o[0]
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
