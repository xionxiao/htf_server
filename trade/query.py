# -*- coding: gbk -*-

from trade import TradeApi
import sys,datetime
sys.path.append("..")
from common.cache import Cache
from common.error import QueryError
from common.utils import dumpUTF8Json,isValidStockCode,round_up_decimal_2
from common.resultbuffer import Result

_cache = Cache()

# 查询类型
QUERY_TYPE = ("资金",  # 0
              "股份",  # 1 
              "当日委托",  # 2
              "当日成交",  # 3
              "可撤单",  # 4
              "股东代码",  # 5
              "融资余额",  # 6
              "融券余额",  # 7
              "可融证券"   # 8
              )

# 历史委托类型
HISTORY_QUERY_TYPE = ("历史委托", # 0
                      "历史成交", # 1
                      "交割单", # 2
                      )

def c_query(u_str, *args, **kwargs):
    api = TradeApi.Instance()
    if u_str in QUERY_TYPE:
        rst = api.Query(u_str, *args, **kwargs)
    if u_str in HISTORY_QUERY_TYPE:
        rst = api.Query(u_str, *args, **kwargs)
    if u_str in ["行情","五档行情","报价"]:
        rst = api.Query("行情", *args, **kwargs)
    if u_str == "涨停价":
        if len(args) == 1:
            assert isValidStockCode(args[0])
            stock = args[0]
        elif len(args) == 0 and kwargs['stock']:
            stock = kwargs['stock']
        hp = _cache.get("五档行情:"+stock+":涨停价")
        if hp:
            return hp
        else:
            rst = _query_quote(stock)            
            hp = round_up_decimal_2(float(rst["昨收价"])*1.1)
            #hp = round_up_decimal_2(float(rst["参考市值价格"])*1.1)
            return hp
    
def _query_quote(stock):
    assert isValidStockCode(stock)
    cc = _cache.get("五档行情:"+stock)
    if cc:
        rst = Result(cc)
        return rst
    else:
        api = TradeApi.Instance()
        try:
            rst = api.GetQuote(stock)
            _cache.set("五档行情:"+rst["证券代码"], str(rst),1)
            now = datetime.datetime.now()
            nextday = datetime.datetime(now.year,now.month,now.day)+datetime.timedelta(days=1)
            expire_seconds = (nextday - now).seconds
            _cache.set("五档行情:"+rst["证券代码"]+":昨收价", rst["昨收价"], expire_seconds)
            harden_price = round_up_decimal_2(float(rst["昨收价"])*1.1)
            _cache.set("五档行情:"+rst["证券代码"]+":涨停价", str(harden_price), expire_seconds)
            return rst
        except QueryError:
            return ""

if __name__ == "__main__":
    api = TradeApi.Instance()
    if not api.isLogon():
        api.Logon("219.143.214.201", 7708, 0, "221199993903", "787878", version="2.19")
    print(c_query("涨停价","000009"))
    r1 = _query_quote("000009")
    #r2 = _query_quote("600036")
    #print(r1["昨收价"] == r2["昨收价"])
    
    
