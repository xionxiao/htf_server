# -*- coding: gbk -*-

from resultbuffer import *
from _stockcode_hashmap import StockCodeHashmap
import re,json,decimal

__all__ = ["Singleton", "StockCode", "round_up_decimal", "isValidStockCode", "isValidIpAddress", "isValidDate",
           "getMarketID","dumpUTF8Json", "c_array"]

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
    
    __FIX_UPPER_STR = ("SH","SS","SZ")
    def __init__(self, code):
        """
        code format: [prefix][code].[suffix]
            preifx: "sh","SH","sz","SZ","ss","SS"
            code: six diggit begen with [0,1,2,3,5,6,7,8,9]
            suffix: "sh","SH","sz","SZ","ss","SS"
            "SS","SH": 沪市
            "SZ": 深市
        e.g. "600036", "sh600036", "600036.sh"
        """
        spstr = code.split('.')
        if len(spstr) > 2 or len(spstr[0]) not in (6,8):
            raise ValueError,"Invalidate stock code " + code
        if len(spstr[0]) == 8 and len(spstr) == 2:
            # prevent "sh600036.sh"
            raise ValueError,"Invalidate stock code " + code

        if len(spstr[0]) == 6:
            self.stock_code = spstr[0]
            if not isValidStockCode(self.stock_code):
                raise ValueError,"Invalidate stock code " + code
            if len(spstr) == 2: # '600036.sh'
                suffix = spstr[1].upper()
                if not suffix in self.__FIX_UPPER_STR:
                    raise ValueError,"Invalidate stock code " + code
                self.market_id = 0 if suffix is 'SZ' else 1
            else: # '600036'
                self.market_id = getMarketID(self.stock_code)

        if len(spstr[0]) == 8:
            if len(spstr) == 2: # invalid "sh600036.sh"
                raise ValueError,"Invalidate stock code " + code
            
            self.stock_code = spstr[0][2:]
            if not isValidStockCode(self.stock_code):
                raise ValueError,"Invalidate stock code " + code
            
            prefix = spstr[0][0:2].upper()
            if not prefix in self.__FIX_UPPER_STR:
                raise ValueError,"Invalidate stock code " + code
            self.market_id = 0 if prefix is "SZ" else 1

    def getMarketId(self, byName=False):
        if byName:
            return "沪市" if self.market_id is 1 else "深市"
        else:
            return self.market_id
    

def isValidStockCode(stock):
    return bool(re.match("[01235678][0-9]{5}$", stock))


def isValidIpAddress(ip):
    if not type(ip) is str:
        return False
    re_str = r'^((\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])\.){3}(\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])$'
    return bool(re.match(re_str, ip))


def isValidDate(date):
    if type(date) is not str:
        return False
    re_str = r'^\d{4}(0\d{1}|1[0-2])([0-2]\d{1}|3[0,1])$'
    return bool(re.match(re_str, date))


def getMarketID(stock, byName=False):
    u""" 判断股票市场： 返回 1-上海  0-深圳  错误代码将弹出异常"""
    if stock[0] in ('5','6'):
        if byName:
            return "沪市"
        return 1
    else: # 0,2,3,5,6,7,8,9 创业板为深圳
        if byName:
            return "深市"
        return 0


def getStockCode(name):
    pass


def getStockName(stock):
    if len(stock) == 6:
        stock += ".SH" if getMarketID(stock) else ".SZ"
    return StockCodeHashmap[stock.upper()]


def c_array(src_list, TYPE):
    assert type(src_list) is list

    count = len(src_list)
    rst = (TYPE*count)()
    for i in range(count): rst[i] = TYPE(src_list[i])
    return rst


def dumpUTF8Json(obj):
    return json.dumps(obj, encoding="gbk").decode('utf8')


def round_up_decimal(number, ndigits=2):
    """ 修复python round()四舍六入问题,默认保留两位小数
        number 可为数字或字符串
    """
    decimal.getcontext().rounding = decimal.ROUND_HALF_UP
    format_str = '{:.' + str(ndigits) + 'f}'
    return float(format_str.format(decimal.Decimal(str(number))))


def printd(obj):
    """Debug print"""
    if type(obj) is ResultBuffer:
        return __print_ResultBuffer(obj)
    if type(obj) is Result:
        return __print_Result(obj)
    if type(obj) is list:
        return __print_list(obj)
    print obj

def __print_list(l):
    for i in l:
        if i not in [Result, ResultBuffer]:
            print str(l).decode('string_escape')
            return
        printd(i)
    print ""

def __print_ResultBuffer(r):
    for i in r:
        printd(i)
    print ""

def __print_Result(r):
    print str(r.attr).decode('string_escape')
    print str(r.items).decode('string_escape')



if __name__ == "__main__":
    print round_up_decimal(6.555)
    print round_up_decimal(6.554)
    print round_up_decimal('6.9955', 2)
    print round_up_decimal('6.9954', 3)
##    test_stock_code = ['300001','600036','000625','100001','6001036','6x0001']
##    for i in test_stock_code:
##        print i,isValidStockCode(i)

    from ctypes import *
    x = [1,2,3]
    p = c_array(x, c_int)

    test_ip_addr = ['10.255.1.255:80', '192.168.1.100', '300.180.260.1','127.0.0.256',10.250]
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

    codes = ['600036','sh600036','000625.sz','ss600036','000001.ss','000001']
    for i in codes:
        sc = StockCode(i)
        print sc.stock_code
        print sc.getMarketId()
        
