#!/usr/bin/env python
# coding=utf-8

import threading,time,sys
from Queue import Queue,PriorityQueue
from vavava.util import LogAdapter
from vavava.basethread import BaseThread
from vavava.base import OBase
#from vavava.util import _interval_timer

_interval_timer = lambda  : time.mktime(time.localtime())

class Task(OBase):
    """ __work      work for Task
        group_id    ??
        begin_time  start time (float)
        interval      interval (float)
    """
    def __init__(self, work, group_id=None, begin_time=None, interval=None):
        self.log         = None
        self.__work      = work
        self.group_id    = group_id
        self.begin_time  = begin_time
        self.interval    = interval
    def set_log(self,log):
        self.log = log
    def __lt__(self, other):
        if self.begin_time and other._begin_time:
            return self.begin_time < other._begin_time
        elif self.begin_time:
            return False
        elif other._begin_time:
            return True
    def __hash__(self):
        return hash(self.begin_time)

class TaskQueue(BaseThread):
    def __init__(self, maxsize=sys.maxint, name="<?wq>",
                 priority_support=False, parent=None, log=None):
        BaseThread.__init__(self,name=name,log=log)
        self.__parent  = parent
        self.__ps      = priority_support
        self.__maxsize = maxsize
        self.__tasks   = PriorityQueue(self.__maxsize)
        self.__mutex   = threading.RLock()

    def Start(self):
        self.running_start()

    def Stop(self,timeout=5):
        self.running_stop()
        self.join(timeout=timeout)

    def do(self, work):
        try:
            work.do(self)
        except Exception as e:
            self.log.exception(e)

    def AddWork(self, work, group_id=-1, begin=None, interval=None):
        if begin is None and interval is None:
            self.do(work)
        else:
            task = Task(work, group_id=group_id, begin_time=begin, interval=interval)
            self._queue_task(task=task)

    def run(self):
        self.log.debug("scheduler routine begin %s", self._group_id)
        while self.IsRunning:
            try:
                tb = _interval_timer()
                #########  process
                self._prepared_task_handler()
                self._done_task_handler()
                #########  process
                te = _interval_timer()
                sleep_interval= 0.05-(te-tb)
                if sleep_interval > 0:
                    time.sleep(sleep_interval)
            except Exception as e:
                self.log.exception(e)
        self.log.debug("scheduler routine end %s", self._group_id)

    def _prepared_task_handler(self):
        if not self._prepared_tasks.empty():
            task = self._prepared_tasks.get()
            self._exec_or_requeue_task(task)

    def _done_task_handler(self):
        task_tmp_list = []
        for tasker in self._taskers:
            if not tasker.doneWorks.empty():
                task_tmp_list.append(tasker.doneWorks.get())
        for task in task_tmp_list:
            self._exec_or_requeue_task(task)

    def _exec_or_requeue_task(self,task):
        now = _interval_timer()
        if task._begin_time and task._begin_time > now:
            self._queue_task(task)
            return False
        elif self._redoable_supoort and task._period:
            task._begin_time = now + task._period
            self.log.warn("[%s] begin=%f,now=%f", self._group_id,task._begin_time,now)
        self.do(task.work)
        return True

    def _queue_task(self,task,internal=True):
        if self._prepared_tasks.full():
            if internal:
                self._task_buf.put(task)
            else:
                raise Exception('task queue is full, try later')
            self.log.warn("[%s] is full can not serve", self._group_id)
        self._prepared_tasks.put(task)

    def __del__(self):
        if self.IsRunning:
            self._running_stop(10)
            self._stop_wqs(10)
            raise Exception("__del__: delete running taskshop [%s]", self._group_id)
