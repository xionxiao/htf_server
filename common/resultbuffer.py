# -*- coding: utf8 -*-

from ctypes import *
from utils import *
import time

__all__ = ["ResultBuffer", "Feedback", "Result", "Error"]


class ResultBuffer(object):

    def __init__(self, count=1):
        assert count > 0
        self._ResultList = []
        if count == 1:
            self.ErrInfo = c_char_p('\000' * 256)
            self.Result = c_char_p('\000' * 1024 * 1024)
            self.Count = 1
        else:
            self.ErrInfo = (c_char_p * count)()
            self.Result = (c_char_p * count)()
            self.Count = count
            for i in range(count):
                self.ErrInfo[i] = c_char_p('\000' * 256)
                self.Result[i] = c_char_p('\000' * 1024 * 1024)

    def __len__(self):
        return self.Count

    def getResults(self):
        # parse only once
        if not self._ResultList:
            if self.Count == 1:
                if self.ErrInfo.value != "":
                    self._ResultList = [
                        Error(self.ErrInfo.value.decode("GBK").encode("UTF8"))]
                else:
                    self._ResultList = [
                        Result(self.Result.value.decode("GBK").encode("UTF8"))]
            else:
                for i in range(self.Count):
                    if self.ErrInfo[i] == "":
                        self._ResultList.append(Result(self.Result[i]))
                    else:
                        self._ResultList.append(Error(self.ErrInfo[i]))
        return self._ResultList

    def __getitem__(self, index):
        """ 返回Result对象 """
        result_list = self.getResults()
        return result_list[index]

    def __nonzero__(self):
        if self.Count == 1:
            return not bool(self.ErrInfo.value)
        for i in range(self.Count):
            if self.ErrInfo[i]:
                return False
        return True


class Feedback(object):

    def __init__(self, result_string):
        self.raw = result_string

    def __nonzero__(self):
        raise NotImplemented

    def __str__(self):
        return self.raw


class Result(Feedback):

    u""" 解析返回结果的二维表格
        Result.attr -> 包含的属性，即表头
        Result[n] -> 返回第n行，结果为dict
        Result[n]["Key"] -> 返回具体内容
        Result["Key"] -> 如果为单行结果，返回Result[0]["Key"]
        Result.raw -> 原始返回字符串
        Result.attr -> 返回keys,等价于Result[0].keys()
        Result.items -> 返回数据的列表，列表的元素为dict
        Result.length -> len(Result) 返回有多少条数据（不包括头）
    """

    def __init__(self, result_string):
        Feedback.__init__(self, result_string)
        self.attr = []  # list of GBK string
        self.items = []  # list of dict
        self.length = 0
        rows = result_string.split('\n')
        self.attr = rows[0].split('\t')
        for row in rows[1:]:
            dic = {}
            row_content = row.split('\t')
            for col in range(len(self.attr)):
                dic[self.attr[col]] = row_content[col]
            self.items.append(dic)
        self.length = len(self.items)

    def __getitem__(self, index):
        if type(index) is int:
            return self.items[index]
        elif len(self) == 1:
            return self.items[0][index]

    def __len__(self):
        return len(self.items)

    def __nonzero__(self):
        if self.attr:  # 只有一行，items=[], length=0
            return True
        else:
            return False

class Error(Feedback):

    def __init__(self, error_string):
        Feedback.__init__(self, error_string)

    def __nonzero__(self):
        return False

    def __str__(self):
        return self.raw

if __name__ == "__main__":
    import sys
    sys.path.append("..")
    from trade import TradeApi
    api = TradeApi.Instance()
    if not api.isLogon():
        api.Logon(
            "219.143.214.201", 7708, 0, "221199993903", "787878", version="2.19")
    try:
        time.sleep(1)
        rst = api.Query("股份")
        print(type(rst))
        print(rst)
        print(type(rst[0]))
        print(rst[0]["证券名称"])
    except Error as e:
        print type(e), e
    finally:
        print "Log off"
        api.Logoff()
