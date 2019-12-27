# -*- coding: utf8 -*-

import unittest
from trade import *


class TestTradeAPI(unittest.TestCase):

    def test_create_instance(self):
        api = TradeApi.Instance()
        self.assertNotEqual(api, None)

    def test_logon(self):
        api = TradeApi.Instance()
        api.Logon("61.132.54.83", 7708, 0,
                  "666622963937", "006096",
                  "", TxPassword="830916", version="6.52")
        self.assertTrue(api.isLogon(), msg=None)

if __name__ == "__main__":
    unittest.main()
