# -*- coding: gbk -*-

from Command import Command
if __name__ == "__main__":
    import sys
    sys.path.append("..")
from trade import TradeApi
from common import printd

class BuyCommand(Command):
    def __init__(self, api, stock, price, share, handler):
        Command.__init__(self, handler)
        self._api = api
        self._stock = stock
        self._price = price
        self._share = share

    def execute(self):
        res = self._api.Buy(self._stock, self._price, self._share)


if __name__ == "__main__":
    api = TradeApi.Instance()
    if not api.isLogon():
        api.Logon("59.173.7.38", 7708, "184039030", "326326")
    buy = BuyCommand(api, "600036", 18.5, 100, None)
    buy.execute()

