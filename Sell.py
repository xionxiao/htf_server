# -*- coding: gbk -*-

from TradeApi import *
import time

def Sell(stock, price, share):
    api = TradeApi()
    api.Open()

    _stock = stock.encode()
    _price = float(price)
    _share = int(share)
    ret_val = ""
    if api.Logon("59.173.7.38", 7708, "184039030", "326326"):
        # ������ͣ��
        rst = api.GetQuote(_stock)
        raising_limit = round(float(rst[1][2]) * 1.1, 2)
        print raising_limit
        
        # �ڿɳ�����ɸѡ��ǰ��Ʊ����ͣ�۸����������
        orders = []
        rst = api.Query("�ɳ���")
        for i in rst:
            if i[1] == _stock and float(i[7]) == raising_limit and i[13] == "��ȯ����":
                orders.append(i[9]) # ί�б��
        
        # �жϹ�Ʊ�Ƿ����
        count = int(_share/100)
        if len(orders) < int(_share/100):
            return u"��Ʊ����"
        
        # �����㣬ѡȡ��Ӧ��������
        print orders[0:count]

        # ����
        rst = api.CancelOrder(orders[0:count])
        if not bool(rst):
            print rst
            return u"����ʧ��"
        
        # ��ʱ0.3ms
        time.sleep(0.3)
        # �µ�
        rst = api.Short(_stock, _price, _share)
        # ���µ�ʧ�ܣ���������ͣ������
        if not bool(rst):
            print rst
            ret_val = u"�µ�ʧ��"
            back = 0
            for i in range(count):
                rst = api.Short(_stock, raising_limit, 100)
                time.sleep(0.2)
                if rst: back += 100
            ret_val += u'\n���� ' + str(back)
            return ret_val
        
        order_id = rst[1][0]
        time.sleep(0.5)
        # ����Ƿ�Ϊ�ϵ�
        rst = api.Query("����ί��")
        for i in rst:
            if i[13] == order_id and i[6] == "�ϵ�":
                ret_val = u"�ϵ�"
                print u"�ϵ�"
                back = 0
                for i in range(count):
                    time.sleep(0.2)
                    print u"����"
                    rst = api.Short(_stock, raising_limit, 100)
                    if rst: back += 100
                ret_val += u'\n���� ' + str(back) 
        if not ret_val:
            ret_val = u"�ѱ������ţ�" + str(order_id)
        
        # ������ʧ�ܣ����ѯ������� (��ʱ����)
        # ������������������� (��ʱ����)
        #print rst

    api.Logoff()
    api.Close()
    return ret_val

if __name__ == "__main__":
    print Sell("601669", 16.80, 300)
    
