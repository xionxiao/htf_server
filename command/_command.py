# -*- coding: utf8 -*-

from threading import Thread
from Queue import Queue

class Receiver(object):
    """ Command callback object """
    def onComplete(self, cmd):
        print("after execute " + str(cmd))

class Command(object):
    def __init__(self, receiver):
        self._receiver = receiver 

    def execute(self):
        self.complete()

    def complete(self):
        if self._receiver:
            self._receiver.onComplete(self)

class Invoker(object):
    def __init__(self):
        pass

    def call(self,cmd):
        print("pre execute " + str(cmd))
        cmd.execute()

class ThreadInvoker(Invoker, Thread):
    def __init__(self, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.workQueue = Queue()
        self.resultQueue = Queue()
        self.setDaemon(True)
        self.start()

    def call(self, cmd):
        self.workQueue.put(cmd)
        return self.resultQueue.get()

    def run(self):
        while True:
            cmd = self.workQueue.get()
            self.resultQueue.put(cmd.execute())

if __name__ == "__main__":
    # TODO: Unit Test
    class BuyCmd(Command):
        def __init__(self, stock, price, share, receiver):
            Command.__init__(self, receiver)

    buy = BuyCmd("600036", 18.5, 100, None)
