#!/usr/bin/env python
# coding=utf-8

if __name__ == '__main__':
    import sys,os
    sys.path.insert(0,'..')

from vavava.workshop import WorkShop
from vavava.util import _interval_timer

class DBWorkshop(WorkShop):
    def __init__(self,dbpool,group="",maxsize=20,minsize=10,redoable_supoort=False,
                 priority_support=False,log=None,parent=None):
        WorkShop.__init__(self,group=group,maxsize=maxsize,minsize=minsize,
                        redoable_supoort=redoable_supoort,
                        priority_support=priority_support,log=log,parent=parent)
        self._db_conns = []
        self._dbpool = dbpool

    def StartWork(self):
        try:
            self.log.debug("Start workshop")
            self._init_workqueues()
            self._init_db_list()
            self._start_wqs()
            self.running_start()
            self.log.debug("Workshop started")
        except Exception as e:
            self.log.exception(e)

    def StopWork(self,timeout=10.0):
        try:
            if __debug__: self.log.debug("[%s] Stop",self.getName())
            self.running_stop()
            self._stop_wqs(timeout)
            self._release_db_list()
            self.join(timeout)
            if self.IsAlive:
                self.log.warn("[%s] thread is not stop!!!![timeout]",self.getName())
            if __debug__: self.log.debug("[%s] Stopped",self.getName())
        except Exception as e:
            self.log.exception(e)

    def _init_db_list(self):
        if self._dbpool:
            for i in range(self._minsize):
                conn = self._dbpool.connection()
                if conn:
                    self._db_conns.append(conn)
                    self._workers[i]._db_conn = conn
                else:
                    for conn in self._db_conns:
                        if conn:
                            conn.close()
                    raise Exception("can not get connection from dbpool")

    def _release_db_list(self):
        for conn in self._db_conns:
            if conn:
                conn.close()
                if __debug__:
                    self.log.debug("retrieve conn")
        self._db_conns = []

####### test .......................

from vavava.workqueue import RedoableWork
import time,MySQLdb
from DBUtils.PooledDB import PooledDB

class TWork(RedoableWork):
    def __init__(self,seq,period,group="",begin_time=None,end_time=None,log=None,name="unnamed-twork"):
        RedoableWork.__init__(self,period=period,group=group,begin_time=begin_time,
            end_time=end_time,log=log,name=name)
        self.seq=seq
        self.times=0

    def do(self,worker=None):
        self.times += 1
        if self._work_param:
            for i in range(10):
                c = self._work_param.cursor()
                if not c:
                    self.log.debug("failed on get cursor")
                else:
                    self.log.debug("get cursor succed")
        else:
            self.log.debug("conn is None")
        self.log.info("[%04d][%03d] working .... %f",self.seq,self.times,_interval_timer() )
        #time.sleep(0.5)

def test1(ws):
    # test for done work buffer full
    while True:
        ws.StartWork()
        index=0
        while index < 100:
            for i in range(10):
                ws.QueueWork(TWork(seq=index,period=10,name="dbworkshop_tester"))
                index += 1
            time.sleep(0.2)
        ws.StopWork()
        time.sleep(0.4)


def test2(ws):
    # test stop work function
    while True:
        ws.StartWork()
        index=0
        while index < 100:
            for i in range(10):
                ws.QueueWork(TWork(seq=index,period=10,name="dbworkshop_tester"))
                index += 1
            time.sleep(0.2)
        ws.StopWork()
        time.sleep(1)

def test3(ws):
    # test stop work function
    ws.StartWork()
    time.sleep(1)
    ws.QueueWork(TWork(seq=1,period=3,name="dbworkshop_tester"))
    while True:
        time.sleep(1)


if __name__ == '__main__':
    import vavava.util
    dbpool = PooledDB(
        MySQLdb,20,50,20,400,False,
        host='localhost',user='tracker',passwd='123',db='tracking',
        charset='utf8'
    )
    log = vavava.util.initlog("./log/test_dbworkshop.log")
    ws = DBWorkshop(dbpool=dbpool,log=log)
    try:
        test3(ws)
        #test2(ws)
    except(KeyboardInterrupt):
        log.info('main thread(%f): User canceled by Ctrl-c',_interval_timer())
    finally:
        log.info('main thread(%f):stop',_interval_timer())
        ws.StopWork()
        log.info('main thread(%f):stopped',_interval_timer())


