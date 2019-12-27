# -*- coding: utf8 -*-

import unittest
from hft.market import *


class TestMarketAPI(unittest.TestCase):

    def test_create_instance(self):
        lv2 = MarketApi.Instance()
        self.assertNotEqual(lv2, None)

    def test_logon(self):
        lv2 = MarketApi.Instance()
        lv2.Connect("61.135.142.90", 443)
        self.assertTrue(lv2.isConnected(), msg=None)

if __name__ == "__main__":
    unittest.main()
