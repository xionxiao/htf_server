# -*- coding: utf8 -*-

from trade import TradeApi
import datetime

try:
    from common.cache import Cache
    from common.utils import isValidStockCode
    from common.utils import round_up_decimal
    from common.resultbuffer import Result
except:
    import sys
    sys.path.append("..")
    from common.cache import Cache
    from common.utils import isValidStockCode
    from common.utils import round_up_decimal
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
HISTORY_QUERY_TYPE = ("历史委托",  # 0
                      "历史成交",  # 1
                      "交割单",  # 2
                      )
# 延时，单位s
_query_timeout = (1,  # "资金"      服务器无限制
                  1,  # "股份"      服务器无限制
                  2,  # "当日委托"    服务器限制30次
                  2,  # "当日成交"    服务器限制30次
                  2,  # "可撤单"     服务器限制30次
                  1,  # "股东代码"    服务器无限制
                  1,  # "融资余额"    服务器无限制
                  1,  # "融券余额"    不支持
                  1,  # "可融证券"    服务器无限制
                  )

_his_query_timeout = (30,  # "历史委托"    服务限制2次
                      6,  # "历史成交"    服务限制10次
                      1,  # "交割单"     服务器无限制
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
    if u_str in ["行情", "五档行情", "报价"]:
        if len(args) == 1:
            assert isValidStockCode(args[0])
            stock = args[0]
        elif len(args) == 0 and kwargs['stock']:
            stock = kwargs['stock']
        else:
            raise(ValueError, "missing stock code")
        return _query_quote(stock)
    if u_str == "涨停价":
        if len(args) == 1:
            assert isValidStockCode(args[0])
            stock = args[0]
        elif len(args) == 0 and kwargs['stock']:
            stock = kwargs['stock']
        else:
            raise(ValueError, "missing stock code")
        hp = _cache.get("五档行情:" + stock + ":涨停价")
        if hp:
            ndigits = len(hp.split('.')[1])
            return round_up_decimal(float(hp), ndigits)
        else:
            rst = _query_quote(stock)
            ndigits = len(rst["昨收价"].split('.')[1])
            hp = round_up_decimal(float(rst["昨收价"]) * 1.1, ndigits)
            # TODO: 周六日，及非开盘时段价格问题
            return hp


def _query_quote(stock):
    assert isValidStockCode(stock)
    cc = _cache.get("五档行情:" + stock)
    if cc:
        rst = Result(cc)
    else:
        api = TradeApi.Instance()
        rst = api.GetQuote(stock)
        _cache.set("五档行情:" + rst["证券代码"], str(rst), 1)
        now = datetime.datetime.now()
        nextday = datetime.datetime(
            now.year, now.month, now.day) + datetime.timedelta(days=1)
        expire_seconds = (nextday - now).seconds
        # TODO: 更新时间与服务器刷新时间不一致
        _cache.set("五档行情:" + rst["证券代码"] + ":昨收价", rst["昨收价"], 60)
        ndigits = len(rst["昨收价"].split('.')[1])
        harden_price = round_up_decimal(float(rst["昨收价"]) * 1.1, ndigits)
        _cache.set(
            "五档行情:" + rst["证券代码"] + ":涨停价", str(harden_price), expire_seconds)
    return rst

if __name__ == "__main__":
    api = TradeApi.Instance()
    if not api.isLogon():
        api.Logon(
            "219.143.214.201", 7708, 0,
            "221199993903", "787878", version="2.19")
    print(c_query("涨停价", "510300"))
    r1 = _query_quote("510300")
    r2 = _query_quote("600150")
    print(r1["昨收价"] == r2["昨收价"])
    print(r2["昨收价"])
    print(c_query("涨停价", "600150"))
    n = 0
    while True:
        n += 1
        print(c_query("历史委托", '20150901', '20150902'), n)
