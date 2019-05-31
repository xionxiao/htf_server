# -*- coding: gbk -*-

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import os

from Buy import Buy
from Sell import Sell
from Cancel import Cancel

from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class QueryHandler(tornado.web.RequestHandler):
    def get(self):
        types = self.get_argument('types')
        print type(types)
        #self.write('query ', types)
        self.finish()

class BuyHandler(tornado.web.RequestHandler):
    def post(self):
        stock = self.get_argument('stock').encode()
        price = self.get_argument('price')
        share = self.get_argument('share')
        self.write(u'买入 ' + str(stock) + "\t" + str(price) + "\t" + str(share) + "\n")
        rst = Buy(stock, price, share)
        self.write(str(rst).decode('gbk'))
        self.finish()

class SellHandler(tornado.web.RequestHandler):
    def post(self):
        stock = self.get_argument('stock').encode()
        price = float(self.get_argument('price'))
        share = int(self.get_argument('share'))
        self.write(u'卖空 ' + str(stock) + "\t" + str(price) + "\t" + str(share) + "\n")
        rst = Sell(stock, price, share)
        print rst
        self.write(rst)
        self.finish()

class CencelHandler(tornado.web.RequestHandler):
    def post(self):
        order = self.get_argument('order').encode()
        self.write(u'撤单 ' + order)
        print type(order)
        print order
        #rst = Cancel(order)
        #self.write(rst)
        self.finish()

class SWServer(tornado.web.Application):
    pass

if __name__ == "__main__":
    tornado.options.parse_command_line()
    settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static").decode('gbk'),
    }
    router = [(r"/", IndexHandler),
              (r"/buy", BuyHandler),
              (r"/sell", SellHandler),
              (r"/cancel", CencelHandler),
              (r"/query", QueryHandler)]
    app = tornado.web.Application(handlers=router, **settings)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
