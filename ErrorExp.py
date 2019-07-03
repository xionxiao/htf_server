# -*- coding: gbk -*-

class ErrorExp(Exception):
    pass

class LogonError(ErrorExp):
    u""" 登录错误 """
    pass

class QueryError(ErrorExp):
    u""" 查询错误 """
    def __init__(self, query_type, error_info, *args, **kwargs):
        # TODO: 处理History Query
        self._query_type = query_type
        self._error_info = error_info

    def __str__(self):
        ret_val = "查询" + self._query_type + "失败: " + self._error_info
        return ret_val

class TradeError(ErrorExp):
    u""" 交易错误 """
    #def __init__(self, orderType, stock, price, quantitiy, priceType):
    pass

