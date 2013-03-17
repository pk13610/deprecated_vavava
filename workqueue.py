#!/usr/bin/env python
# coding=utf-8

import threading,time,sys
from Queue import Queue,PriorityQueue
from vavava.util import LogAdapter
from vavava.basethread import BaseThread
from vavava.base import OBase
from vavava.util import _interval_timer

class Work(OBase):
    """
    base class for user-work-item,self.do() must be written over
    For priority work: you need to overwrite __lt__ and __hash__
    """
    def __init__(self, log=None, name="<?work>", *args, **kwargs ):
        OBase.__init__(self, name=name)
        self.done     = False
        self.__param  = None
        self.__args   = args
        self.__kwargs = kwargs
        self.setLogger(log)
    def do(self,worker=None):
        pass
    def _do(self,worker=None):
        try:
            self.done=True
            self.do(worker)
        except Exception as e:
            self.log.exception(e)
        except:
            pass
    def add_work_to_parent(self, work):
        if self.__parent:
            self.__parent.QueueWork(work)
        else:
            raise Exception("GeneratorWork has no parent handle")
    def get_instance(self,xml):
        pass
    def setLogger(self, log):
        self.log = LogAdapter(log)

class WorkQueue(BaseThread):
    def __init__(self, maxsize=sys.maxint, name="<?wq>",
                 redoable_support=False, parent=None, log=None):
        BaseThread.__init__(self, name=name,log=log)
        self.__parent = parent
        self.__rs = redoable_support
        self.__maxsize = maxsize
        self.__works = Queue(self.__maxsize)
        self.doneWorks = Queue(self.__maxsize)
        self.__mutex = threading.RLock()
        self.param = None

    def run(self):
        while self.IsRunning:
            try:
                tb = _interval_timer()
                if not self.__works.empty() and not self.IsPaused:
                    work = self.__works.get(block=True,timeout=0.5)
                    work._do(worker=self) # working ...
                    if self.__rs and not work.done:
                        if self.doneWorks.full():
                            self.doneWorks.get() # drop top when buffer is full
                            self.log.warn("[%s] Work buffer is full,drop top work.", self.getName())
                        self.doneWorks.put(work)
                else:
                    te = _interval_timer()
                    sleep_interval= 0.05 - te + tb
                    if sleep_interval > 0:
                        time.sleep(sleep_interval)
            except Exception as e:
                self.log.exception(e)
                time.sleep(0.5)

    def Start(self):
        self.running_start()

    def Pause(self,timeout=10.0):
        self.running_pause()

    def Resume(self):
        self.running_resume()

    def Stop(self,timeout=10.0,flush=True):
        if __debug__ :
            self.log.debug("Stopped queue.%s", self.getName())
        self.running_stop()
        self.join(timeout)
        if self.IsAlive:
            self.log.warn("[%s] thread is not stop!!!![timeout]", self.getName())
        if flush:
            self.__works   = Queue(self.__maxsize)
            self.doneWorks = Queue(self.__maxsize)
        self.log.debug("Stopped with %d work in queue. (flush=%d)", self.__works.qsize(),flush)

    def QueueWork(self,work):
        if not self.IsAlive:
            self.log.warn("Queue stopped when new work come.")
            return
        try:
            if work:
                work.setLogger(self.log)
                self.__works.put(item=work)
        except Exception as e:
            self.log.exception(e)

    @property
    def IsWorking(self):
        # running and has work to do means "working"
        return self.IsAlive and self.IsRunning and not self.__works.empty()

    def GetInfo(self):
        self.__mutex.acquire()
        info = WorkQueue.WorkQueueInfo(
            self.getName(),
            self.__rs,
            self.__works.qsize(),
            self.doneWorks.qsize()
        )
        self.__mutex.release()
        return info

    def GetWorkQueueInfo(self):
        info = []
        self.__mutex.acquire()
        if self.__works.not_empty:
            for i in range(self.__works.qsize()):
                w = self.__works.get()
                info.append([
                    w.in_queue_seq,
                    w.getName(),
                    w._begin_time
                ])
        self.__mutex.release()
        return info

    class WorkQueueInfo:
        def __init__(self, Name, Priority_support,
                     InQueueSize, DoneWorkSize ):
            self.Name               =    Name
            self.Priority_support   =    Priority_support
            self.InQueueSize        =    InQueueSize
            self.DoneWorkSize       =    DoneWorkSize

