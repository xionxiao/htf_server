# -*- coding: gbk -*-

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import os

from Buy import Buy
from Sell import Sell
from Cancel import Cancel
from GetStockPool import getStockPool
from QueryOrderList import queryOrderList
from InstantSell import InstantSell

from StockPool import *

from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class QueryHandler(tornado.web.RequestHandler):
    def get(self):
        catalogues = self.get_argument('catalogues')
        if catalogues == u"stockpool":
            rst = getStockPool()
            self.write(rst)
        if catalogues == u"orderlist":
            rst = queryOrderList()
            self.write(rst)
        self.finish()

class BuyHandler(tornado.web.RequestHandler):
    def post(self):
        stock = self.get_argument('stock').encode()
        price = self.get_argument('price')
        share = self.get_argument('share')
        try:
            float(price)
            int(share)
        except:
            self.write(u"参数错误")
            self.finish()
            return
                
        self.write(u'买入 ' + str(stock) + "\t" + str(price) + "\t" + str(share) + "\t\n")
        rst = Buy(stock, price, share)
        self.write(rst)
        self.finish()

class SellHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            stock = self.get_argument('stock').encode()
            price = float(self.get_argument('price'))
            share = int(self.get_argument('share'))
        except:
            self.write(u"参数错误")
            self.finish()
            return
        self.write(u'卖空 ' + str(stock) + "\t" + str(price) + "\t" + str(share) + "\t\n")
        rst = Sell(stock, price, share)
        self.write(rst)
        self.finish()

class InstantSellHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            stock = self.get_argument('stock').encode()
            share = int(self.get_argument('share'))
        except:
            self.write(u"参数错误")
            self.finish()
            return
        self.write(u'即时卖空 ' + str(stock) + "\t" + "\t" + str(share) + "\n")
        rst = InstantSell(stock, share)
        self.write(rst)
        self.finish()

class CencelHandler(tornado.web.RequestHandler):
    def post(self):
        order = self.get_argument('order').encode()
        self.write(u'撤单 ' + order)
        rst = Cancel(order)
        self.write(rst)
        self.finish()

class SWServer(tornado.web.Application):
    pass

if __name__ == "__main__":
    api = TradeApi()
    api.Open()
    rst = api.Logon("59.173.7.38", 7708, "184039030", "326326")
    if not rst:
        print rst
    sp = StockPool(api)
    
    tornado.options.parse_command_line()
    settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static").decode('gbk'),
    }
    router = [(r"/", IndexHandler),
              (r"/buy", BuyHandler),
              (r"/sell", SellHandler),
              (r"/instant_sell", InstantSellHandler),
              (r"/cancel", CencelHandler),
              (r"/query", QueryHandler)]
    app = tornado.web.Application(handlers=router, **settings)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
