#!/usr/bin/env python
# coding=utf-8


from vavava.workqueue import WorkQueue, Work
from vavava.scheduler import Scheduler, Task
import time

class TestWork(Work):
    def __init__(self,seq):
        Work.__init__(self, name = "test_work")
        self.seq = seq
    def do(self,worker=None):
        self.log.info("[%s] %d in", self.getName(), self.seq)
        time.sleep(0.5)
        self.log.info("[%s] %d out", self.getName(), self.seq)

def test_workqueue(log):
    wq = WorkQueue(name = "work_queue", redoable_support = True, log = log)
    try:
        seq = 0
        wq.Start()
        for i in range(10):
            tgw = TestWork(seq=seq)
            wq.QueueWork(work=tgw)
            seq += 1
        while True:
            log.info("wq is running ................")
            time.sleep(1)

        log.info('main thread(%f):stop', _interval_timer())
        wq.Stop()
        log.info('main thread(%f):stopped', _interval_timer())
    except(KeyboardInterrupt):
        log.info('main thread(%f): User canceled by Ctrl-c', _interval_timer())
    finally:
        log.info('main thread(%f):stop', _interval_timer())
        wq.Stop()
        log.info('main thread(%f):stopped', _interval_timer())



if __name__ == '__main__':
    from vavava.util import _interval_timer, initlog
    log = initlog("./log/test_all.log")
    ###################################################
    test_workqueue(log)
    ###################################################

