# -*- coding: gbk -*-

from ctypes import *
from decimal import *
from ResultBuffer import *

def round_up_decimal_2(float_number):
    """ 修复python round()四舍六入问题,保留两位小数 """
    getcontext().rounding = ROUND_HALF_UP 
    return float('{:.2f}'.format(Decimal(str(float_number))))

def c_array(src_list, TYPE):
    if type(src_list) is not list: return
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
    x = round_up_decimal_2(44.665)
    print x
