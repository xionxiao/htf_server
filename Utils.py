# -*- coding: gbk -*-

from decimal import *

def round_up_decimal_2(float_number):
    """ 修复python round()四舍六入问题,保留两位小数 """
    getcontext().rounding = ROUND_HALF_UP 
    return float('{:.2f}'.format(Decimal(str(float_number))))


if __name__ == "__main__":
    x = round_up_decimal_2(44.665)
    print x
