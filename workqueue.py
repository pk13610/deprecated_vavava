#!/usr/bin/env python
# coding=utf-8

if __name__ == '__main__':
    """ for file debug"""
    import sys,os
    sys.path.insert(0,os.path.join( os.getcwd(), '..' ))

__author__ = 'vavava'


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
    def __init__(self, period=None, group="", begin_time=None,
                 end_time=None, log=None, name="<?work>", *args, **kwargs ):
        OBase.__init__(self,name=name)
        self.log          = LogAdapter(log)
        #self._work_name   = name
        self._group_id    = group
        self._done        = False
        self._redoable    = False
        self._begin_time  = begin_time
        self._end_time    = end_time
        self._period      = period
        self._db_conn     = None
        self._args        = args
        self._kwargs      = kwargs
        self._serial_id_  = None  # specify id for serial works,
                                  # in order to run these works in the same thread

    def init(self,period=None, group="", begin_time=None,
             end_time=None, log=None, name="<?work>", *args, **kwargs):
        self.log          = LogAdapter(log)
        self._group_id    = group
        self._begin_time  = begin_time
        self._end_time    = end_time
        self._period      = period
        self._args        = args
        self._kwargs      = kwargs
        self.setName(name)

    def do(self,worker=None):
        pass

    def _do(self,worker=None):
        try:
            self._done=True
            self.do(worker)
        except Exception as e:
            self.log.error("delete work:group=%s,name=%s,%s",self._group_id,self._name,e)
            self.log.exception(e)
        except:
            pass

    def add_work_to_parent(self,work):
        if self._wq_parent:
            self._wq_parent.QueueWork(work)
        else:
            raise Exception("GeneratorWork has no parent handle")

    def get_instance(self,xml):
        pass

    def __lt__(self, other):
        if self._begin_time and other._begin_time:
            return self._begin_time < other._begin_time
        elif self._begin_time:
            return False
        elif other._begin_time:
            return True

    def __hash__(self):
        return hash(self._begin_time)

class RedoableWork(Work):
    def __init__( self, period, group="", begin_time=None, end_time=None,
                 log=None, name="<?>", *args, **kwargs ):
        Work.__init__( self, period=period, group=group, begin_time=begin_time,
            end_time=end_time, log=log, name=name, args=args, kwargs=kwargs )
        self._redoable=True

    def _do(self,worker=None):
        self.do(worker)
        self._done=False

class WorkQueue(BaseThread):

    def __init__(self,maxsize=sys.maxint,name="<?wq>",redoable_support=False,
                 priority_support=False, parent=None,log=None):
        BaseThread.__init__(self,name=name,log=log)
        self._wq_parent = parent
        self._redoable_support = redoable_support
        self._priority_support = priority_support
        if self._priority_support:
            self.works = PriorityQueue(maxsize)
            self.doneWorks = PriorityQueue(maxsize)
        else:
            self.works = Queue(maxsize)
            self.doneWorks = Queue(maxsize)
        self.maxsize = maxsize
        self._mutex=threading.RLock()
        self.last_working_time=None
        self._db_conn = None

    def run(self):
        while self.IsRunning:
            try:
                tb = _interval_timer()
                if not self.works.empty() and not self.IsPaused:
                    work = self.works.get(block=True,timeout=0.5)
                    work._do(worker=self) # working ...
                    #if __debug__: self.log.debug("[%s] work(%s) func out"%(self.getName(),work._work_name))
                    if self._redoable_support and not work._done:
                        if self.doneWorks.full():
                            self.doneWorks.get() # drop top when buffer is full
                            self.log.warn("[%s] Work buffer is full,drop top work.", self.getName())
                        #if __debug__: self.log.warn("[%s] add a redo work."%work._work_name )
                        self.doneWorks.put(work)
                else:
                    te = _interval_timer()
                    sleep_interval= 0.05 - te + tb
                    if sleep_interval > 0:
                        time.sleep(sleep_interval)
            except Exception as e:
                self.log.exception(e)
                time.sleep(0.5)

    def wq_start(self):
        self.running_start()

    def wq_pause(self,timeout=10.0):
        self.running_pause()

    def wq_resume(self):
        self.running_resume()

    def wq_stop(self,timeout=10.0,flush=True):
        if __debug__ :
            self.log.debug("Stopped queue.%s", self.getName())
        self.running_stop()
        self.join(timeout)
        if self.IsAlive:
            self.log.warn("[%s] thread is not stop!!!![timeout]", self.getName())
        if flush:
            self._flush_works()
        if __debug__ :
            self.log.debug("Stopped with %d work in queue. (flush=%d)", self.works.qsize(),flush)

    def QueueWork(self,work):
        if not self.IsAlive:
            self.log.warn("Queue stopped when new work come.")
            return
        try:
            if work:
                work.log = self.log
                self.works.put(item=work)
        except Exception as e:
            self.log.exception(e)

    def _flush_works(self):
        n = self.works.qsize()
        if n > 0:
            for i in range(n):
                self.works.get()
        m = self.doneWorks.qsize()
        if m > 0:
            for i in range(m):
                self.doneWorks.get()
        if __debug__ :
            self.log.debug("Flush workqueue (works=%d,doneWorks=%d)."
                ,self.works.qsize(), self.doneWorks.qsize() )

    @property
    def IsWorking(self):
        # running and has work to do means "working"
        return self.IsAlive and self.IsRunning and not self.works.empty()

    def GetInfo(self):
        self._mutex.acquire()
        info = WorkQueue.WorkQueueInfo(
            self.getName(),
            self._redoable_support,
            self._priority_support,
            self.works.qsize(),
            self.doneWorks.qsize(),
            self.last_working_time
        )
        self._mutex.release()
        return info

    class WorkQueueInfo:
        def __init__(self, Name, Redoable_support, Priority_support,
                     InQueueSize, DoneWorkSize, lastWorkingTime ):
            self.Name               =    Name
            self.Redoable_support   =    Redoable_support
            self.Priority_support   =    Priority_support
            self.InQueueSize        =    InQueueSize
            self.DoneWorkSize       =    DoneWorkSize
            self.lastWorkingTime    =    lastWorkingTime

class handler_base:
    HANDLE_ID=0
    def _before_start(self):pass
    def _after_stop(self):pass
    def _before_run(self):pass
    def _after_run(self):pass

# test code  .............

class MyWork(Work):
    def __init__(self,seq=0,period=None,group="",
                 begin_time=None,end_time=None,log=None,name="MyWork"):
        Work.__init__(self,period=period,group=group,
            begin_time=begin_time,end_time=end_time,log=log,name=name)
        self.seq=seq

    def do(self,worker):
        import time
        self.log.info("[%05d] Hello DB, am %s !!!!!!!  %f",self.seq,worker.getName(), _interval_timer())

class MyRedoableWork(RedoableWork):
    def __init__(self,period,seq=0,group="",begin_time=None,end_time=None,log=None,name="MyWork"):
        RedoableWork.__init__(self,period=period,group=group,
            begin_time=begin_time,end_time=end_time,log=log,name=name)
        self.seq=seq

    def do(self,worker):
        import time
        self.log.info("[%05d] Hello DB, am %s !!!!!!!  %f", self.seq,worker.getName(), _interval_timer())
        self._done = False

class MyPriorityWork(Work):
    def __init__(self,seq=0,period=None,group="",
                 begin_time=None,end_time=None,log=None,name="MyWork"):
        Work.__init__(self,period=period,group=group,
            begin_time=begin_time,end_time=end_time,log=log,name=name)
        self.seq=seq

    def do(self,worker):
        import time
        self.log.info("[%05d] Hello DB, am %s !!!!!!!  %f", self.seq,worker.getName(), _interval_timer())

    def __lt__(self, other):
        return self.seq < other.seq

    def __hash__(self):
        return hash(self.seq)

def test1(workingLine,log):
    log.info('test for process of work buffer is full (%f)',_interval_timer())
    workingLine=WorkQueue(name="test_worker",log=log)
    workingLine.wq_start()
    seq=0
    while seq < 1000:
        for i in range(20):
            seq += 1
            log.info("Add a work : %d",seq)
            wr=MyRedoableWork(seq=seq,period=10,name="testwork")
            workingLine.QueueWork(wr)
        time.sleep(1)

def test2(workingLine,log):
    log.info('test for all start (%f)',_interval_timer())
    workingLine=WorkQueue(name="test_worker",log=log)
    workingLine.wq_start()
    import time
    seq=0
    while seq < 10:
        seq += 1
        log.info("Add a work : %d"%seq)
        workingLine.QueueWork(MyWork(seq=seq,name="testwork"))
    workingLine.wq_pause()  # restart .........
    log.info('main thread(%f):paused',_interval_timer())
    time.sleep(5)
    workingLine.wq_resume()  # restart .........
    log.info('main thread(%f):resumed',_interval_timer())
    while seq < 100:
        seq += 1
        log.info("Add a work : %d"%seq)
        workingLine.QueueWork(MyWork(seq=seq,name="testwork"))
        time.sleep(1)

def test3(workingLine,log):
    log.info('test for priority work start (%f)',_interval_timer())
    # test for priority work
    workingLine=WorkQueue(priority_support=True,name="test_worker",log=log)
    workingLine.wq_start()
    seq=1000
    while seq > 0:
        for i in range(20):
            seq -= 1
            log.info("Add a work : %d",seq)
            wr=MyPriorityWork(seq=seq,log=log,name="testwork")
            workingLine.QueueWork(wr)
        time.sleep(1)

if __name__ == '__main__':
    import vavava.util
    log = vavava.util.initlog("./log/test_workqueue.log")
    workingLine = WorkQueue()
    try:
        test1(workingLine,log)
    except(KeyboardInterrupt):
        log.info('main thread(%f):stop',_interval_timer())
        workingLine.wq_stop(timeout=5,flush=True)
        log.info('main thread(%f):stopped',_interval_timer())


