# -*- coding: gbk -*-

from ctypes import *
from Utils import *
from ResultBuffer import *
import datetime
import time

class Order(object):
    # ȯ��
    _securiies_trader = None
    # �ɶ�����
    _stock_holder_code = None
    # �������ͣ�������־��
    _type = None
    # ���۷�ʽ
    _price_type = None
    # �ɶ�����
    _stockholder_code = None
    # ��Ʊ����
    _stock_code = None
    # ����
    _shares = None
    # �µ�ʱ��
    _place_time = None
    # ����״̬
    _order_status
    # ί�б��
    # �ɽ����
    # ����ԱID
