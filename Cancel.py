# -*- coding: gbk -*-

from TradeApi import *
from Utils import *
from Cache import *
import time

def Cancel(order_id):
    api = TradeApi()
    if not api.isLogon():
        api.Open()
        api.Logon("59.173.7.38", 7708, "184039030", "326326")
    cache = Cache()
    rst = api.Query("�ɳ���")
    order = None
    ret_val = ""
    if not rst:
        return u"��ѯ�ɳ�����ʧ��"
    # ����rst, �ҵ���Ӧ��order����
    if order_id in rst[0]["ί�б��"]:
        index = rst[0]["ί�б��"].index(order_id)
        order = rst[0][index]
    else:
        return u"û�д˶���" + str(order_id)

    flag = order[4]
    # �ж���������
    if flag == "����":
        rst = api.CancelOrder(order_id)
        if not bool(rst):
            return u"����ʧ�ܣ�\n"
        else:
            return u"�����ɹ���\n"
    elif flag == "����":
        rst = api.CancelOrder(order_id)
        # ��������ɹ�
        if bool(rst):
            time.sleep(0.3)
            # ��õ�ǰ��ͣ��
            price = cache.get(order[1],"��ͣ��")
            # ��ͣ���µ�
            rst = api.Short(order[1], price, int(float(order[8])))
            if rst:
                ret_val = u"�����ɹ������� " + order[8]
            else:
                ret_val = u"�����ɹ�, ����ʧ�� " + str(rst)
        else:
            ret_val = u"����ʧ�ܣ�\n" + str(rst).decode('string_escape')

    return ret_val

if __name__ == "__main__":
    print Cancel("196")
    
