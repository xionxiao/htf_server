# -*- coding: gbk -*-

from ctypes import *
from Utils import *
from ResultBuffer import *
import datetime
import time

class Order(object):
    # 券商
    _securiies_trader = None
    # 股东代码
    _stock_holder_code = None
    # 订单类型（买卖标志）
    _type = None
    # 报价方式
    _price_type = None
    # 股东代码
    _stockholder_code = None
    # 股票代码
    _stock_code = None
    # 股数
    _shares = None
    # 下单时间
    _place_time = None
    # 订单状态
    _order_status
    # 委托编号
    # 成交编号
    # 交易员ID
