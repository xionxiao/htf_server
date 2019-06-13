# -*- coding: gbk -*-

from ctypes import *
from decimal import *
from ResultBuffer import *
import re

class Singleton(object):
  """ 单例模式 """
  __instance=None
  def __init__(self):
    pass
  
  def __new__(cls,*args,**kwd):
    if not isinstance(cls.__instance, cls):
      cls.__instance=object.__new__(cls,*args,**kwd)
    return cls.__instance

class SingletonDecorater:
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

def isValidStockCode(stock):
    if not type(stock) is str:
        return False
    return bool(re.match("[036][0-9]{5}$", stock))

def round_up_decimal_2(float_number):
    """ 修复python round()四舍六入问题,保留两位小数 """
    getcontext().rounding = ROUND_HALF_UP 
    return float('{:.2f}'.format(Decimal(str(float_number))))

def c_array(src_list, TYPE):
    assert(type(src_list) is list)

    count = len(src_list)
    rst = (TYPE*count)()
    for i in range(count): rst[i] = TYPE(src_list[i])
    return rst

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
    print str(r.head).decode('string_escape')
    print str(r.table).decode('string_escape')



if __name__ == "__main__":
##    x = round_up_decimal_2(44.665)
##    print x
##    test_stock_code = ['300001','600036','000625','100001','6001036','6x0001']
##    for i in test_stock_code:
##        print i,isValidStockCode(i)

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
        
