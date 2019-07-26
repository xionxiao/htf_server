# -*- coding: gbk -*-

from trade import TradeApi
import sys,datetime
sys.path.append("..")
from common.cache import Cache
from common.error import QueryError
from common.utils import dumpUTF8Json,isValidStockCode,round_up_decimal_2
from common.resultbuffer import Result

_cache = Cache()

# ��ѯ����
QUERY_TYPE = ("�ʽ�",  # 0
              "�ɷ�",  # 1 
              "����ί��",  # 2
              "���ճɽ�",  # 3
              "�ɳ���",  # 4
              "�ɶ�����",  # 5
              "�������",  # 6
              "��ȯ���",  # 7
              "����֤ȯ"   # 8
              )

# ��ʷί������
HISTORY_QUERY_TYPE = ("��ʷί��", # 0
                      "��ʷ�ɽ�", # 1
                      "���", # 2
                      )

def c_query(u_str, *args, **kwargs):
    api = TradeApi.Instance()
    if u_str in QUERY_TYPE:
        rst = api.Query(u_str, *args, **kwargs)
    if u_str in HISTORY_QUERY_TYPE:
        rst = api.Query(u_str, *args, **kwargs)
    if u_str in ["����","�嵵����","����"]:
        rst = api.Query("����", *args, **kwargs)
    if u_str == "��ͣ��":
        if len(args) == 1:
            assert isValidStockCode(args[0])
            stock = args[0]
        elif len(args) == 0 and kwargs['stock']:
            stock = kwargs['stock']
        hp = _cache.get("�嵵����:"+stock+":��ͣ��")
        if hp:
            return hp
        else:
            rst = _query_quote(stock)            
            hp = round_up_decimal_2(float(rst["���ռ�"])*1.1)
            #hp = round_up_decimal_2(float(rst["�ο���ֵ�۸�"])*1.1)
            return hp
    
def _query_quote(stock):
    assert isValidStockCode(stock)
    cc = _cache.get("�嵵����:"+stock)
    if cc:
        rst = Result(cc)
        return rst
    else:
        api = TradeApi.Instance()
        try:
            rst = api.GetQuote(stock)
            _cache.set("�嵵����:"+rst["֤ȯ����"], str(rst),1)
            now = datetime.datetime.now()
            nextday = datetime.datetime(now.year,now.month,now.day)+datetime.timedelta(days=1)
            expire_seconds = (nextday - now).seconds
            _cache.set("�嵵����:"+rst["֤ȯ����"]+":���ռ�", rst["���ռ�"], expire_seconds)
            harden_price = round_up_decimal_2(float(rst["���ռ�"])*1.1)
            _cache.set("�嵵����:"+rst["֤ȯ����"]+":��ͣ��", str(harden_price), expire_seconds)
            return rst
        except QueryError:
            return ""

if __name__ == "__main__":
    api = TradeApi.Instance()
    if not api.isLogon():
        api.Logon("219.143.214.201", 7708, 0, "221199993903", "787878", version="2.19")
    print(c_query("��ͣ��","000009"))
    r1 = _query_quote("000009")
    #r2 = _query_quote("600036")
    #print(r1["���ռ�"] == r2["���ռ�"])
    
    
