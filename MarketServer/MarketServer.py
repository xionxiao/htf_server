# -*- coding: gbk -*-

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import sys,os,json
sys.path.append("..")

from command import *
from common.utils import dumpUTF8Json
from common.error import *
from query_cmd import *
from market import MarketApi

from tornado.options import define, options
define("port", default=80, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("html\\index.html")

class QueryHandler(tornado.web.RequestHandler, Receiver):
    _invoker = Invoker()
    @tornado.web.asynchronous
    def get(self):
        try:
            catalogues = self.get_argument('catalogues')
            if catalogues == u"quote10":
                stocks = self.get_argument('stocks').encode()
                stocks = stocks.split(',')
                cmd = QueryQuote10Cmd(stocks, self)
                self._invoker.call(cmd)
            if catalogues == u"quote5":
                stocks = self.get_argument('stocks').encode()
                stocks = stocks.split(',')
                cmd = QueryQuote5Cmd(stocks, self)
                self._invoker.call(cmd)
            if catalogues == u"transaction_detail":
                stock = self.get_argument('stock').encode()
                cmd = QueryTransactionDetailCmd(stock, self)
                self._invoker.call(cmd)
            if catalogues == u"transaction":
                stock = self.get_argument('stock').encode()
                cmd = QueryTransactionCmd(stock, self)
                self._invoker.call(cmd)
            if catalogues == u"minute":
                stock = self.get_argument('stock').encode()
                cmd = QueryMinuteTimeDataCmd(stock, self)
                self._invoker.call(cmd)
        finally:
            pass
            #self.finish()

    def onComplete(self, cmd):
        self.finish()


class MarketServer(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        tornado.web.Application.__init__(self, *args, **kwargs)
        self._lv2_api = MarketApi.Instance()
        self._lv2_api.Connect("119.97.185.4", 7709)

if __name__ == "__main__":
    api = MarketApi.Instance()
    api.Connect("119.97.185.4",7709)
    
    tornado.options.parse_command_line()
    settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "html").decode('gbk'),
    "debug": True
    }
    router = [(r"/", IndexHandler),
              (r"/query", QueryHandler)]
    app = MarketServer(handlers=router, **settings)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
