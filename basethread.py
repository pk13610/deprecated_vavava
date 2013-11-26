#!/usr/bin/env python
# coding=utf-8

# if __name__ == '__main__':
#     """ for file debug"""
#     import sys,os
#     sys.path.insert(0,os.path.join( os.getcwd(), '..' ))

import threading
from threading import Thread,Event,Lock
from vavava.util import LogAdapter,_interval_timer

__author__ = 'vavava'
"""
usage:
    while self.IsRunning:
        if not self.IsPaused:
            ....
            do something
            ....
        else:
            wait for a while
"""


class BaseThread(object):
    def __init__(self, name="<?thread>", log=None):
        self._name = name
        self._thread = None
        self.log = LogAdapter(log)
        self._is_paused=threading.Event()
        self._is_paused.clear()
        self._is_running=threading.Event()
        self._is_running.clear()

    def _run(self,*_args, **_kwargs):
        self.run()
        self._is_running.clear()
        self._is_paused.clear()

    def run(self):
        """
        usage:
            while self.IsRunning:
                if not self.IsPaused:
                    ....
                    do something
                    ....
                else:
                    wait for a while
        """

    def running_start(self):
        if not self.IsRunning:
            self._is_running.set()
            if self._thread:
                if self._thread.isAlive:
                    raise Exception("can not start more than once")

            self._thread = Thread(
                group   = None,
                target  = self._run,
                name    = self._name,
                args    = (),
                kwargs  = {},
                verbose = None
            )
            self._thread.setDaemon(True)
            self._thread.start()
        else:
            raise Exception("can not start more than once")

    def running_stop(self):
        if self._is_running.is_set():
            self._is_running.clear()
            if self._is_paused.is_set():
                self._is_paused.clear()
        elif self._thread:
            # maybe running stop,but thread is not over
            raise Exception("thread is not running")

    def join(self,timeout=10.0):
        if self._thread:
            self._thread.join(timeout)
            self._thread = None

    def running_pause(self):
        if self.IsPaused:
            raise Exception("thread already paused")
        self._is_paused.set()

    def running_resume(self):
        if self.IsPaused:
            self._is_paused.clear()
        else:
            raise Exception("thread already resumed")

    def getName(self):
        return self._name

    @property
    def IsAlive(self):
        # thread is alive, maybe paused, maybe running
        # thread is not alive: surely not running
        return self._thread and self._thread.is_alive() and self.IsRunning

    @property
    def IsRunning(self):
        # thread is running: maybe paused, surely alive
        # thread is not running: out of work routine
        return self._is_running.is_set()

    @property
    def IsPaused(self):
        return self._is_paused.is_set()

    def __del__(self):
        if self.IsRunning:
            self.running_stop()
            raise Exception("thread is running on __del__")




# test .................................................

class TThread(BaseThread):
    def __init__(self,seq,log):
        BaseThread.__init__(self,log=log)
        self.seq=seq

    def run(self):
        while self.IsRunning:
            if self.IsPaused:
                import time
                self.log.debug("_thread waiting %d ",self.seq)
                time.sleep(1)
            else:
                self.log.debug("_thread running %d ",self.seq)
        self.log.debug("_thread out %d",self.seq)

def test1(log):
    import time
    tt1=TThread(seq=1,log=log)
    try:
        while True:
            log.debug('main _thread(%f):start',_interval_timer())
            tt1.running_start()
            time.sleep(0.4)
            tt1.running_stop()
            tt1.join(1)
            time.sleep(1)
    except(KeyboardInterrupt):
        log.debug('main _thread(%f):stop timer',_interval_timer())
        tt1.running_stop()
        tt1.join(1)
        #tt2.stop()
        #tt3.stop()
        log.debug('main _thread(%f):stopped',_interval_timer())


def test2(log):
    import time
    tt1=TThread(seq=1,log=log)
    #tt2=TThread(2)
    #tt3=TThread(3)

    log.debug('main _thread(%f):start',_interval_timer())
    tt1.running_start()
    #tt2.start()
    #tt3.start()
    try:
        while True:
            if not tt1.IsPaused:
                tt1.running_pause()
            else:
                tt1.running_resume()
            time.sleep(2)
    except(KeyboardInterrupt):
        log.debug('main _thread(%f):stop timer',_interval_timer())
        tt1.running_stop()
        #tt2.stop()
        #tt3.stop()
        log.debug('main _thread(%f):stopped',_interval_timer())

if __name__ == '__main__':
    import vavava.util
    log = vavava.util.initlog("./log/test_dbworkshop.log")
    test2(log)

