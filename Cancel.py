# -*- coding: gbk -*-

from TradeApi import *
from Utils import *
import time

def Cancel(order_id):
    api = TradeApi()
    api.Open()
    api.Logon("59.173.7.38", 7708, "184039030", "326326")
    rst = api.Query("�ɳ���")
    order = None
    ret_val = ""
    # ����rst, �ҵ���Ӧ��order����
    for i in rst:
        if i[9] == order_id:
            order = i
            break

    # û�ҵ�����
    if not order:
        return u"û�иö���:" + str(order_id)

    flag = order[4]
    # �ж���������
    if flag == "����":
        rst = api.CancelOrder(order_id)
        if not bool(rst):
            return u"����ʧ�ܣ�\n" + str(rst).decode('string_escape')
        else:
            return u"�����ɹ���\n" + str(rst).decode('string_escape')
    elif flag == "����":
        rst = api.CancelOrder(order_id)
        print bool(rst)
        # ��������ɹ�
        if bool(rst):
            time.sleep(0.3)
            # ��õ�ǰ��ͣ��
            print order[1]
            rst = api.Query("����", str(order[1]))
            price = round_up_decimal_2(float(rst[1][2]) * 1.1)
            print price
            back_amount = 0
            # ��ͣ���µ�
            for x in range(int(float(order[8]))/100):
                time.sleep(0.2)
                rst = api.Short(i[1], price, 100)
                back_amount += 100
            ret_val = u"�����ɹ�,���� " + str(back_amount)
        else:
            ret_val = u"����ʧ�ܣ�\n" + str(rst).decode('string_escape')

    api.Logoff()
    api.Close()
    return ret_val

if __name__ == "__main__":
    print Cancel("3890")
    
