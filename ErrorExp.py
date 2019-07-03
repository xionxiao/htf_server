# -*- coding: gbk -*-

class ErrorExp(Exception):
    pass

class LogonError(ErrorExp):
    u""" ��¼���� """
    pass

class QueryError(ErrorExp):
    u""" ��ѯ���� """
    def __init__(self, query_type, error_info, *args, **kwargs):
        # TODO: ����History Query
        self._query_type = query_type
        self._error_info = error_info

    def __str__(self):
        ret_val = "��ѯ" + self._query_type + "ʧ��: " + self._error_info
        return ret_val

class TradeError(ErrorExp):
    u""" ���״��� """
    #def __init__(self, orderType, stock, price, quantitiy, priceType):
    pass

