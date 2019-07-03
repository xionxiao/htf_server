# -*- coding: gbk -*-
import datetime

class ErrorExp(Exception):
    def __init__(self, feedback, **kwargs):
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.feedback = feedback
        self.extra = kwargs

    def __str__(self):
        return str(self.feedback)

class LogonError(ErrorExp):
    u""" 登录错误 """
    def __init__(self, ip, port, feedback, **kwargs):
        ErrorExp.__init__(self, feedback, **kwargs)
        self.ip = ip
        self.port = port

    def __str__(self):
        return str(self.feedback)

class QueryError(ErrorExp):
    u""" 查询错误 """
    # TODO: query_type统一定义
    def __init__(self, query_type, feedback, **kwargs):
        ErrorExp.__init__(self, feedback, **kwargs)
        self.query_type = query_type

    def __str__(self):
        ret_val = "Query " + str(self.query_type) + " failed:\n    " + str(self.feedback) + "\n"
        if self.extra:
            ret_val += "with:\n    " + str(self.extra)
        return ret_val

class BatchQueryError(QueryError):
    u""" 批量查询错误 """
    # TODO: 批量查询额外数据处理
    pass

class TradeError(ErrorExp):
    u""" 交易错误 """
    def __init__(self, order_type, stock, price, shares, price_type, feedback, **kwargs):
        ErrorExp.__init__(self, feedback, **kwargs)
        self.param = {}
        self.param["order_type"] = order_type
        self.param["stock"] = stock
        self.param["price"] = price
        self.param["shares"] = shares
        self.param["price_type"] = price_type

class BatchTradeError(TradeError):
    u""" 批量交易错误 """
    # TODO: 批量单错误额外数据处理
    pass

class CancelError(ErrorExp):
    pass

class RepayError(ErrorExp):
    pass

if __name__ == "__main__":
    q = QueryError("行情", "hello", hello="world")
    print q
