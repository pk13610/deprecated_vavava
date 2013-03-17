#!/usr/bin/env python
# coding=utf-8

if __name__ == '__main__':
    """ for file debug"""
    import sys,os
    sys.path.insert(0,os.path.join( os.getcwd(), '..' ))

from threading import Thread,Event
from vavava.util import LogAdapter
from vavava.basethread import BaseThread
import time
__author__ = 'vavava'

class LoopTimer(BaseThread):
    """Call a function after a specified number of seconds:

    t = Looper(30.0, f, args=[], kwargs={})
    t.start()
    t.cancel() # stop the timer's action if it's still waiting
    """

    def __init__(self, interval=1.0, accuracy=0.01,function=None, log=None, args=(), kwargs={}):
        BaseThread.__init__(self,log)
        self.log = LogAdapter(log)
        self._interval = interval
        self._accuracy = accuracy
        self._func = function
        self._args = args
        self._kwargs = kwargs

    def do(self):
        self.is_active.clear()
        is_first_run=True
        start=0.0
        now=0.0
        tmp=0.0
        while self.IsActive:
            now = time.clock()
            interval = now - start
            assert(interval>0)
            if start == 0.0 or interval > self._interval:
                if tmp < interval: tmp = interval
                self.log.debug("LoopTimer current interval = %f (%f)"%(interval,tmp))
                start = now
                if self._func:
                    self.log.debug("LoopTimer.func started")
                    self._func()
                    self.log.debug("LoopTimer.func ended")
                else:
                    self.log.warn("LoopTimer has no target to run")
            else:
                self.is_active.wait(timeout=self._accuracy)

        self.is_active.set()

class Timer(LoopTimer):
    def __init__(self,period_s=1.0):
        LoopTimer.__init__(self, interval=period_s, accuracy=0.001, function=self.func)
        self.interval=0

    def func(self):
        import time
        now = time.clock()
        if self.interval != 0:
            self.interval = now - self.interval
        print('timer is running:%f'%self.interval)
        self.interval = now

def main():
    import time
    timer = Timer()
    print('main thread(%f):start'%time.clock())
    timer.running_start()
    try:
        while True:
            time.sleep(1)
            t = time.localtime()
            print('main thread(%f):waiting'%time.clock())
    except(KeyboardInterrupt):
        print('main thread(%f):stop timer'%time.clock())
        timer.running_stop()
        print('main thread(%f):stopped'%time.clock())

if __name__ == '__main__':
    main()

