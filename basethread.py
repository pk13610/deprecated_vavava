#!/usr/bin/env python
# coding=utf-8

import threading
from threading import Thread,Event,Lock
from vavava.util import get_logger

class BaseThread(object):
    def __init__(self, name="<?thread>", log=None):
        self._name = name
        self._thread = None
        self.log = get_logger(log)
        self._is_paused=threading.Event()
        self._is_paused.clear()
        self._is_running=threading.Event()
        self._is_running.clear()

    def _run(self,*_args, **_kwargs):
        self.run()
        self._is_running.clear()
        self._is_paused.clear()

    def run(self):
        pass

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
