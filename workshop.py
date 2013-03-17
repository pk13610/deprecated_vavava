#!/usr/bin/env python
# coding=utf-8

if __name__ == '__main__':
    """ for file debug"""
    import sys,os
    sys.path.insert(0,os.path.join( os.getcwd(), '..' ))

__author__ = 'vavava'

import threading,time,os
from Queue import PriorityQueue,Queue
from vavava.workqueue import WorkQueue
from vavava.basethread import BaseThread

# time.clock() performance different on win and linux
if os.name == "nt":
    from time import clock as _interval_timer
else:
    from time import time as _interval_timer

class WorkShop(BaseThread):

    def __init__(self,group="",maxsize=20,minsize=10,redoable_supoort=False,
                 priority_support=False,log=None,parent=None):
        BaseThread.__init__(self,name="WorkShop",log=log)
        self._parent   = parent
        self._group_id = group
        self._minsize  = minsize
        self._maxsize  = maxsize
        self._redoable_supoort = redoable_supoort
        self._priority_support = priority_support
        self._dispatch_cursor = 0
        self._mutex = threading.RLock()
        self._workers=[]
        if priority_support:
            self._prepared_works = PriorityQueue()
            self._work_buf = PriorityQueue() # buffer when _prepared_works full
        else:
            self._prepared_works = Queue()
            self._work_buf = Queue()

    def StartWork(self):
        try:
            self.log.debug("Start workshop %s", self._group_id )
            self._init_workqueues()
            self._start_wqs()
            self.running_start()
            self.log.debug("Workshop started %s", self._group_id )
        except Exception as e:
            self.log.exception(e)

    def StopWork(self,timeout=10.0):
        # ????????
        try:
            if __debug__: self.log.debug("[%s] Stop", self._group_id)

            self.running_stop()
            self._stop_wqs(timeout)
            self.join(timeout)
            if self.IsAlive:
                self.log.warn("[%s] thread is not stop!!!![timeout]", self._group_id)

            if __debug__: self.log.debug("[%s] Stopped", self._group_id)
        except Exception as e:
            self.log.exception(e)

    def RestartWork(self,timeout=30.0):
        # ????????
        self.StopWork(timeout)
        self.StartWork(timeout)

    def PauseWork(self,timeout=30.0):
        self.thread_pause()

    def ResumeWork(self,timeout=30.0):
        self.thread_resume()

    def QueueWork(self,work):
        # __eql__able check ????
        if work:
            self._queue_work(work,False)

    def IsWorkRedoable(self):
        self._mutex.acquire()
        tof = self._redoable_supoort
        self._mutex.release()
        return tof

    class WorkShopInfo:
        def __init__(self,infos,prepared_work_size,buffered_work_size):
            self.infos = infos
            self.prepared_work_size = prepared_work_size
            self.buffered_work_size = buffered_work_size

    def GetInfo(self):
        infos = []
        self._mutex.acquire()
        try:
            for worker in self._workers:
                infos.append(worker.GetInfo())
        except Exception as e:
            self.log.exception(e)
            raise e
        self._mutex.release()
        return WorkShop.WorkShopInfo(
            infos,self._prepared_works.qsize(),self._work_buf.qsize())

    def _init_workqueues(self):
        self._workers = []
        for i in range(self._minsize):
            self._workers.append(
                WorkQueue(
                    name="WQ_%d"%i,
                    priority_support=self._priority_support,
                    redoable_support=self._redoable_supoort,
                    parent=self,
                    log=self.log
                )
            )

    def _start_wqs(self):
        for work in self._workers:
            if not work.IsAlive:
                work.wq_start()

    def _stop_wqs(self,timeout=30.0):
        # timeout for each work line
        if __debug__ : self.log.debug("_stop_wqs in %s", self._group_id)
        for i in range(len(self._workers)):
            line=self._workers[i]
            if line.IsAlive:
                line.wq_stop(timeout=timeout,flush=False)
        if __debug__ : self.log.debug("_stop_wqs out %s", self._group_id)

    def run(self):
        self.log.debug("workshop routine begin %s", self._group_id)
        while self.IsRunning:
            try:
                tb = _interval_timer()
                #########  process
                self._prepared_work_handler()
                self._done_work_handler()
                #########  process
                te = _interval_timer()
                sleep_interval= 0.05-(te-tb)
                if sleep_interval > 0:
                    time.sleep(sleep_interval)
            except Exception as e:
                self.log.exception(e)
                raise

        self.log.debug("workshop routine end %s", self._group_id)

    def _prepared_work_handler(self):
        if not self._prepared_works.empty():
            work=self._prepared_works.get()
            self._exec_or_requeue_work(work)

    def _done_work_handler(self):
        # collect done-works and re-queue or queue to exec queue
        if not self._redoable_supoort:
            return
        work_tmp_list = []
        for worker in self._workers:
            if not worker.doneWorks.empty():
                work_tmp_list.append(worker.doneWorks.get()) # grab all for once is needed  ???? 20121115
        for work in work_tmp_list:
            self._exec_or_requeue_work(work)

    def _exec_or_requeue_work(self,work):
        # insert work into execute queue, otherwise re-queue it
        if not self._priority_support:
            self._insert_work_to_exec_queue(work)
            return True
        now = _interval_timer()
        if work._begin_time and work._begin_time > now:
            self._queue_work(work)
            return False
        elif self._redoable_supoort and work._period:
            work._begin_time = now + work._period
            self.log.warn("[%s] begin=%f,now=%f", self._group_id,work._begin_time,now)
        self._insert_work_to_exec_queue(work)
        return True

    def _queue_work(self,work,internal=True):
        if self._prepared_works.full():
            if internal:
                self._work_buf.put(work)
            else:
                raise Exception('work queue is full, try later')
            self.log.warn("[%s] is full can not serve", self._group_id)
        self._prepared_works.put(work)

    def _insert_work_to_exec_queue(self,work):
        index = 0
        if self._minsize == 1:
            index = 0
        elif work._serial_id_ is not None:
            index = work._serial_id_%(self._minsize)
        else:
            self._mutex.acquire()
            index = self._dispatch_cursor%(self._minsize)
            self._dispatch_cursor += 1
            self._mutex.release()
        self._workers[index].QueueWork(work)

    def __del__(self):
        if self.IsRunning:
            self._running_stop(10)
            self._stop_wqs(10)
            raise Exception("__del__: delete running workshop [%s]", self._group_id)

####### test .......................

from vavava.workqueue import MyWork,MyRedoableWork,MyPriorityWork


def test1(ws,log):
    log.info("test for done work buffer full")
    index=110
    ws = WorkShop(log=log)
    while True:
        ws.StartWork()
        while index > 0:
            for i in range(10):
                ws.QueueWork(MyWork(seq=index,period=10,log=log))
                index -= 1
            time.sleep(0.8)
        ws.StopWork()
        time.sleep(0.5)


def test2(ws,log):
    log.info("test for priority support")
    ws = WorkShop(priority_support=True,redoable_supoort=True,log=log)
    ws.StartWork()
    index=1100
    while index > 0:
        for i in range(50):
            ws.QueueWork(MyPriorityWork(seq=index,period=10,log=log))
            index -= 1
        time.sleep(1)

def test3(ws,log):
    log.info("test for function")
    ws = WorkShop(redoable_supoort=True,priority_support=True,log=log)
    ws.StartWork()
    ws.QueueWork(MyRedoableWork(seq=1,period=3,log=log))
    while 1:
        time.sleep(1)

def test4(ws,log):
    log.info("test for redoable support")
    ws = WorkShop(priority_support=True,redoable_supoort=True,log=log)
    ws.StartWork()
    time.sleep(1)
    ws.QueueWork(MyRedoableWork(seq=1,period=3,log=log))
    while True:
        infos = []
        infos = ws.GetInfo()
        for info in infos.infos:
            if info.DoneWorkSize > 0:
                log.info("%s->doneworkQueue=%d",info.Name, info.DoneWorkSize)
        time.sleep(1)

if __name__ == '__main__':
    import vavava.util
    log = vavava.util.initlog("./log/test_workshop.log")
    ws = WorkShop()
    try:
        test4(ws,log)
    except(KeyboardInterrupt):
        log.error('main thread(%f): User canceled by Ctrl-c', _interval_timer())
    finally:
        log.info('main thread(%f):stop', _interval_timer())
        ws.StopWork()
        log.info('main thread(%f):stopped', _interval_timer())



