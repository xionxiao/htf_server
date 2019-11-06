# -*- coding: utf8 -*-

from resultbuffer import *
from _stockcode_hashmap import StockCodeHashmap
import re
import json
import decimal

__all__ = ["Singleton", "StockCode", "round_up_decimal",
           "isValidStockCode", "isValidIpAddress", "isValidDate",
           "getMarketID", "dumpUTF8Json", "c_array"]


class Singleton:

    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


class StockCode(object):

    """ fields:
            stock_code: 000001,600036,000625
            market_id: 1-上海，0-深圳
    """

    __PREFIX_SUFFUX_UPPER_STR = ("SH", "SS", "SZ")

    def __init__(self, code, market=None):
        """
        code format: [prefix][code].[suffix]
            preifx: "sh","SH","sz","SZ","ss","SS"
            code: six diggit begen with [0,1,2,3,5,6,7,8,9]
            suffix: "sh","SH","sz","SZ","ss","SS"
            "SS","SH": 上海，1
            "SZ": 深圳，0
        e.g. "600036", "sh600036", "600036.sh"
        """
        # Copy constructure
        if type(code) is StockCode:
            self.stock_code = code.stock_code
            self.market_id = code.market_id
            return

        if str(market).upper() in ('0', "SZ", "深圳", u"深圳"):
            self.market_id = 0
            self.stock_code = code
        elif str(market).upper() in ('1', 'SS', 'SH', "上海", u"上海"):
            self.market_id = 1
            self.stock_code = code
        else:  # market_id = None
            spstr = code.split('.')
            if len(code) > 9 or len(spstr) > 2 or len(spstr[0]) not in (6, 8):
                raise(ValueError, "Invalidate stock code " + code)
            if len(spstr[0]) == 6:
                self.stock_code = spstr[0]
                if len(spstr) == 2:  # '600036.sh'
                    suffix = spstr[1].upper()
                    if suffix not in self.__PREFIX_SUFFUX_UPPER_STR:
                        raise(ValueError, "Invalidate stock code " + code)
                    self.market_id = 0 if suffix == 'SZ' else 1
                else:  # '600036'
                    self.market_id = getMarketID(self.stock_code)

            if len(spstr[0]) == 8:
                if len(spstr) == 2:  # invalid "sh600036.sh"
                    raise(ValueError, "Invalidate stock code " + code)
                self.stock_code = spstr[0][2:]
                prefix = spstr[0][0:2].upper()
                if prefix not in self.__PREFIX_SUFFUX_UPPER_STR:
                    raise(ValueError, "Invalidate stock code " + code)
                self.market_id = 0 if prefix == "SZ" else 1

        if not isValidStockCode(self.stock_code):
            raise(ValueError, "Invalidate stock code " + code)

        if self.format() not in StockCodeHashmap:
            raise(ValueError, "do not have stock code " + code)

    def __str__(self):
        return self.format()

    def getMarketSuffix(self):
        return "SH" if self.market_id == 1 else "SZ"

    def format(self, suffix=True, prefix=False):
        if suffix:
            return self.stock_code + "." + self.getMarketSuffix()
        elif prefix:
            return self.getMarketSuffix() + self.stock_code
        else:
            return self.stock_code

    def getMarketId(self):
        return self.market_id

    def getStockCode(self):
        return self.stock_code

    def getStockName(self):
        return StockCodeHashmap[self.format()]

    def getMarketName(self):
        return "上海" if self.market_id == 1 else "深圳"


def isValidStockCode(stock):
    return bool(re.match("[012356789][0-9]{5}$", stock))


def isValidIpAddress(ip):
    if not type(ip) is str:
        return False
    re_str =r'^((\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])\.){3}(\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])$'
    return bool(re.match(re_str, ip))


def isValidDate(date):
    if type(date) is not str:
        return False
    re_str = r'^\d{4}(0\d{1}|1[0-2])([0-2]\d{1}|3[0,1])$'
    return bool(re.match(re_str, date))


def getMarketID(stock, byName=False):
    u""" 判断股票市场： 返回 1-上海  0-深圳  错误代码将弹出异常"""
    if stock[0] in ('5', '6'):
        if byName:
            return "上海"
        return 1
    else:  # 0,2,3,5,6,7,8,9 创业板为深圳
        if byName:
            return "深圳"
        return 0


def c_array(src_list, TYPE):
    assert type(src_list) is list

    count = len(src_list)
    rst = (TYPE * count)()
    for i in range(count):
        rst[i] = TYPE(src_list[i])
    return rst


def dumpUTF8Json(obj):
    # return json.dumps(obj, encoding="gbk").decode('utf8')
    return json.dumps(obj)


def round_up_decimal(number, ndigits=2):
    """ 修复python round()四舍六入问题,默认保留两位小数
        number 可为数字或字符串
    """
    decimal.getcontext().rounding = decimal.ROUND_HALF_UP
    format_str = '{:.' + str(ndigits) + 'f}'
    return float(format_str.format(decimal.Decimal(str(number))))


if __name__ == "__main__":
    print round_up_decimal(6.555)
    print round_up_decimal(6.554)
    print round_up_decimal('6.9955', 2)
    print round_up_decimal('6.9954', 3)
# test_stock_code = ['300001','600036','000625','100001','6001036','6x0001']
# for i in test_stock_code:
# print i,isValidStockCode(i)

    from ctypes import *
    x = [1, 2, 3]
    p = c_array(x, c_int)

    test_ip_addr = ['10.255.1.255:80', '192.168.1.100',
                    '300.180.260.1', '127.0.0.256', 10.250]
    for i in test_ip_addr:
        print i, isValidIpAddress(i)

    @Singleton
    class Class1():

        def __init__(self):
            print "Class1 __init__"

    @Singleton
    class Class2():

        def __init__(self):
            print "Class2 __init__"

    c1 = Class1.Instance()
    c2 = Class2.Instance()
    c11 = Class1.Instance()
    c22 = Class2.Instance()

    print(c1)

    codes = ['600036', 'sh600036', '000625.sz', '900916.SH',
             'ss600036', '000001.ss', '000001', "600036.SZ"]
    for i in codes:
        sc = StockCode(i)
        print sc.stock_code
        print sc
        print sc.format(suffix=False, prefix=True)
        print unicode(sc.getStockName(), 'utf8')
        print unicode(sc.getMarketName(), 'utf8')
