# -*- coding: gbk -*-

from ctypes import *
import datetime
import time

def c_array(src_list, TYPE):
    if type(src_list) is not list: return
    count = len(src_list)
    rst = (TYPE*count)()
    for i in range(count): rst[i] = TYPE(src_list[i])
    return rst

class ResultBuffer(object):
    def __init__(self, count=1):
        assert count > 0
        if count == 1:
            self.ErrInfo = c_char_p('\000'*256)
            self.Result = c_char_p('\000'*1024*1024)
            self.count = 1
        else:
            self.ErrInfo = (c_char_p*count)()
            self.Result = (c_char_p*count)()
            self.count = count
            for i in range(count):
                self.ErrInfo[i] = c_char_p('\000'*256)
                self.Result[i] = c_char_p('\000'*1024*1024)

    def __len__(self):
        return self.count

    _ResultList = []
    def _parseResult(self):
        if not self._ResultList:
            if self.count == 1:
                self._ResultList = [ResultTable(self.Result.value)]
            else:
                self._ResultList = [ ResultTable(i) for i in self.Result ]
        return self._ResultList

    _ErrorList = []
    def _parseError(self):
        if not self._ErrorList:
            if self.count == 1:
                self._ErrorList = [ self.ErrInfo.value ]
            else:
                self._ErrorList = [ i for i in self.ErrInfo ]
        return self._ErrorList
        
    def __getitem__(self, index):
        """返回Result对象"""
        assert type(index) is int
        assert index >= 0
        # Return result
        if bool(self): 
            result_list = self._parseResult()
            return result_list[index]
        # Return Error
        else:
            error_list = self._parseError()
            return error_list[index]

    def __nonzero__(self):
        if type(self.ErrInfo) is c_char_p:
            return self.ErrInfo.value == ""
        else:
            err = [ not bool(i) for i in self.ErrInfo ]
            return bool(sum(err))

class ResultTable(object):
    """返回表格"""
    def __init__(self, result_string):
        rows = result_string.split('\n')
        tab = [ r.split('\t') for r in rows ]
        if not len(tab) == 1:
            # ["表头1","表头2"]
            self._table_head = [i.decode('gbk') for i in tab[0]]
            # [[第一行],[第二行],...]
            self._table = tab[1:]
            # {"表头":[元素列表]}
            self._col = {}
            for i in self._table_head:
                self._col[i] = []
            for r in self._table:
                for i in range(len(self._table_head)):
                    c = r[i].decode('gbk') if i<len(r) else u""
                    self._col[self._table_head[i]].append(c)
        else:
            # 处理非表格格式
            self._table_head = []
            self._table = [tab[0][0].decode('gbk')]
            self._col = {}

    def __getitem__(self, name_or_index):
        if type(name_or_index) is int:
            return self._table[name_or_index]
        elif name_or_index in self._table_head:
            return self._col[name_or_index]

    def head(self):
        """返回表头"""
        return self._table_head

def printl(l):
    print(str(l).decode('gbk'))
    
if __name__ == "__main__":
    from TradeApi import TradeApi
    api = TradeApi()
    api.Open()
    rst = api.Logon("59.173.7.38", 7708, "184039030", "326326")
    print bool(rst)
    rst = api.Query("行情", zqdm=['600036','600036'])
    printl(rst[0].head())
    printl(rst[0][0])
    print(rst[0][u'证券名称'][0])
    #r = Result(rst.Result.value)
    #printl(r.attr())
    #printl(r[0])
