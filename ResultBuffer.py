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
        if count == 1:
            self.ErrInfo = c_char_p('\000'*256)
            self.Result = c_char_p('\000'*1024*1024)
            self.count = 1
        elif count > 1:
            self.ErrInfo = (c_char_p*count)()
            self.Result = (c_char_p*count)()
            self.count = count
            for i in range(count):
                self.ErrInfo[i] = c_char_p('\000'*256)
                self.Result[i] = c_char_p('\000'*1024*1024)

    def __len__(self):
        return self.count

    def _makeTable(self, tab_str):
        rows = tab_str.split('\n')
        tab = [ r.split('\t') for r in rows ]
        return tab
        
    def __getitem__(self, name):
        rst = ["Result", "result"]
        if name in rst:
            if type(self.Result) is c_char_p:
                return [self._makeTable(self.Result.value)]
            else:
                return [self._makeTable(i) for i in self.Result]
        err = ["ErrInfo", "errInfo", "error", "Error"]
        if name in err:
            if type(self.ErrInfo) is c_char_p:
                return [self.ErrInfo.value]
            else:
                return [i for i in self.ErrInfo]
        if type(name) is int:
            if not bool(self):
                return self["Error"][name]
            else:
                if type(self.Result) is c_char_p:
                    return self['Result'][0][name]
                else:
                    return self['Result'][name]
                    

    def __nonzero__(self):
        if type(self.ErrInfo) is c_char_p:
            return self.ErrInfo.value == ""
        else:
            err = [ not bool(i) for i in self.ErrInfo ]
            return bool(sum(err))

    def __str__(self):
        if bool(self):
            ss = ""
            for i in self['Result']:
                for j in i:
                    ss += str(j).decode('string_escape')+'\n'
            return ss
        else:
            return str(self['Error']).decode('string_escape')


class Result(object):
    def __init__(self, result_string):
        rows = result_string.split('\n')
        tab = [ r.split('\t') for r in rows ]
        if len(tab) == 1:
            raise Exception("fail to construct Result")
        self._table_head = tab[0]
        self._table = tab[1:]
        self._value = {}
        for i in self._table_head:
            self._value[i] = []
        for r in self._table:
            for i in range(len(self._table_head)):
                c = r[i] if i<len(r) else ""
                self._value[self._table_head[i]].append(c)

    def __getitem__(self, name_or_index):
        if type(name_or_index) is int:
            return self._table[name_or_index]
        elif name_or_index in self._table_head:
            return self._value[name_or_index]

    def attr(self):
        return self._table_head

def printl(l):
    """打印list"""
    print(str(l).decode('string_escape'))
    
if __name__ == "__main__":
    from TradeApi import TradeApi
    api = TradeApi()
    api.Open()
    api.Logon("119.147.80.108", 443, "184039030", "326326")
    rst = api.Query("资金")
    r = Result(rst.Result.value)
    printl(r.attr())
    printl(r[0])
    printl(r['证券代码'])
