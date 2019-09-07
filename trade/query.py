# -*- coding: gbk -*-

from trade import TradeApi
import sys,datetime
sys.path.append("..")
from common.cache import Cache
from common.utils import dumpUTF8Json,isValidStockCode,round_up_decimal
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
# ��ʱ����λs
_query_timeout = (1, #"�ʽ�"      ������������
                  1, #"�ɷ�"      ������������
                  2, #"����ί��"    ����������30��
                  2, #"���ճɽ�"    ����������30��
                  2, #"�ɳ���"     ����������30��
                  1, #"�ɶ�����"    ������������
                  1, #"�������"    ������������
                  1, #"��ȯ���"    ��֧��
                  1, #"����֤ȯ"    ������������
                  )

_his_query_timeout = (30, #"��ʷί��"    ��������2��
                      6, #"��ʷ�ɽ�"    ��������10��
                      1, #"���"     ������������
                      )

def c_query(u_str, *args, **kwargs):
    if u_str in QUERY_TYPE:
        cc = _cache.get(u_str)
        if cc:
            rst = Result(cc)
        else:
            api = TradeApi.Instance()
            rst = api.Query(u_str, *args, **kwargs)
            index = QUERY_TYPE.index(u_str)
            _cache.set(u_str, str(rst), _query_timeout[index])
        return rst
    if u_str in HISTORY_QUERY_TYPE:
        cc = _cache.get(u_str)
        if cc:
            rst = Result(cc)
        else:
            api = TradeApi.Instance()
            rst = api.Query(u_str, *args, **kwargs)
            index = HISTORY_QUERY_TYPE.index(u_str)
            _cache.set(u_str, str(rst), _his_query_timeout[index])
        return rst
    if u_str in ["����","�嵵����","����"]:
        if len(args) == 1:
            assert isValidStockCode(args[0])
            stock = args[0]
        elif len(args) == 0 and kwargs['stock']:
            stock = kwargs['stock']
        else:
            raise ValueError, "missing stock code"
        return _query_quote(stock)
    if u_str == "��ͣ��":
        if len(args) == 1:
            assert isValidStockCode(args[0])
            stock = args[0]
        elif len(args) == 0 and kwargs['stock']:
            stock = kwargs['stock']
        else:
            raise ValueError, "missing stock code"
        hp = _cache.get("�嵵����:"+stock+":��ͣ��")
        if hp:
            ndigits = len(hp.split('.')[1])
            return round_up_decimal(float(hp), ndigits)
        else:
            rst = _query_quote(stock)            
            ndigits = len(rst["���ռ�"].split('.')[1])
            hp = round_up_decimal(float(rst["���ռ�"])*1.1, ndigits)
            # TODO: �����գ����ǿ���ʱ�μ۸�����
            return hp
    
def _query_quote(stock):
    assert isValidStockCode(stock)
    cc = _cache.get("�嵵����:"+stock)
    if cc:
        rst = Result(cc)
    else:
        api = TradeApi.Instance()
        rst = api.GetQuote(stock)
        _cache.set("�嵵����:"+rst["֤ȯ����"], str(rst), 1)
        now = datetime.datetime.now()
        nextday = datetime.datetime(now.year,now.month,now.day)+datetime.timedelta(days=1)
        expire_seconds = (nextday - now).seconds
        # TODO: ����ʱ���������ˢ��ʱ�䲻һ��
        _cache.set("�嵵����:"+rst["֤ȯ����"]+":���ռ�", rst["���ռ�"], 60)
        ndigits = len(rst["���ռ�"].split('.')[1])
        harden_price = round_up_decimal(float(rst["���ռ�"])*1.1, ndigits)
        _cache.set("�嵵����:"+rst["֤ȯ����"]+":��ͣ��", str(harden_price), expire_seconds)
    return rst

if __name__ == "__main__":
    api = TradeApi.Instance()
    if not api.isLogon():
        api.Logon("219.143.214.201", 7708, 0, "221199993903", "787878", version="2.19")
    print(c_query("��ͣ��","510300"))
    r1 = _query_quote("510300")
    r2 = _query_quote("600150")
    print(r1["���ռ�"] == r2["���ռ�"])
    print(r2["���ռ�"])
    print(c_query("��ͣ��","600150"))
    n = 0
    while True:
        n += 1
        print(c_query("��ʷί��", '20150901','20150902'), n)
    
    
