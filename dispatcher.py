#!/usr/bin/env python
# coding=utf-8

if __name__ == '__main__':
    """ for file debug"""
    import sys,os
    sys.path.insert(0,os.path.join( os.getcwd(), '..' ))

import time
import vavava.basethread
import vavava.util

__author__ = 'vavava'

class Dispatcher(vavava.basethread.BaseThread):
    def __init__(self,workshops={},name="<?dsp>",log=None):
        vavava.basethread.BaseThread.__init__(self,name=name,log=log)
        self._workshops = workshops

    def AddWorkshop(self,ws,start=True):
        if not ws:
            raise Exception( 'invalid param ws,None "None" value is needed')
        if ws._group_id in self._workshops:
            raise Exception( 'invalid workshop by group_id='.join(ws._group_id))
        self._workshops[ws._group_id]=ws
        if start:
            ws.StartWork()

    def ActivateWorkshop(self,group_id):
        if not group_id or group_id == "":
            raise Exception( 'invalid param group_id,None "None" value is needed')
        ws = self._workshops.get(group_id)
        if not ws:
            raise Exception( 'workshop not found (group_id=%s)'%group_id)
        if ws.IsAlive:
            return  # not an exception
        ws.StartWork()

    def DeactivateWorkshop(self,group_id):
        if not group_id or group_id == "":
            raise Exception( 'invalid param group_id,None "None" value is needed')
        ws = self._workshops.get(group_id)
        if not ws:
            raise Exception( 'workshop not found (group_id=%s)'%group_id)
        if not ws.IsAlive:
            return  # not an exception
        ws.StopWork()

    def ActivateAllWorkshops(self):
        for group_id in self._workshops:
            workshop = self._workshops[group_id]
            if not workshop:
                raise Exception( 'workshop not found (group_id=%s)'%group_id)
            if workshop.IsAlive:
                return  # not an exception
            workshop.StartWork()

    def DeactivateAllWorkshops(self):
        for group_id in self._workshops:
            workshop = self._workshops[group_id]
            if not workshop:
                raise Exception( 'workshop not found (group_id=%s)'%group_id)
            if not workshop.IsAlive:
                continue  # not an exception
            workshop.StopWork()

    def AddWork(self,work):
        if work is None:
            raise Exception("invalid param")
        if not work._group_id or work._group_id == "":
            return False
        ws = self._workshops.get(work._group_id)
        if not ws:
            self.log.warn("[dispatcher] unknown groupid %d", work._group_id )
            return False
        ws.QueueWork(work)
        return True

    def ActivateMonitor(self):
        try:
            self.log.debug("[%s] Start",self.getName())
            self.running_start()
            self.log.debug("[%s]  Started",self.getName())
        except Exception as e:
            self.log.exception(e)

    def DeactivateMonitor(self,timeout=30.0):
        self.log.debug("[%s] Stop",self.getName())
        self.running_stop()
        self.join(timeout)
        if self.is_alive():
            self.log.warn("[%s] Thread is not stop!!!![timeout]",self.getName())
        else:
            self.log.debug("[%s] Stopped",self.getName())

    def GetInfo(self):
        info_str = ""
        for workshop in self._workshops:
            sw = self._workshops[workshop]
            wsinfo = sw.GetInfo()
            info_str += "  Monitor(%s,%d,%d):" % \
                        ( sw._group_id,wsinfo.prepared_work_size,wsinfo.buffered_work_size)
            for info in wsinfo.infos:
                info_str += "[%s|%d|%d]"%(info.Name,info.InQueueSize, info.DoneWorkSize)
        self.log.info(info_str)

# test ...............
"""
from vavava.workqueue import Work,RedoableWork
class AddWorkWork(RedoableWork):
    def __init__(self,begin_time=None,end_time=None,period=None,log=None,name="<?test>"):
        RedoableWork.__init__(self,begin_time,end_time,period,log,name)

    def do(self,worker):
        self.dispatcher = None
        if worker and worker._parent and worker._parent._parent:
            self.dispatcher = worker._parent._parent
        # do you things with self.dispatcher....
        # eg: self.dispatcher.AddWork(work)
        self.add_works()

    def add_works(self):
        pass


import vavava.base
from vavava.workqueue import RedoableWork

class TWork(RedoableWork):
    def __init__(self,id=0,begin_time=None,end_time=None,period=None,log=None,name=""):
        RedoableWork.__init__(self,begin_time,end_time,period,log,name)
        self.id = id
        self.invoke_times=0

    def do(self,worker=None):
        self.invoke_times += 1
        self.log.debug("[%04d][%03d] working %f",self.id,self.invoke_times,time.time())
        """
        if self.invoke_times > 2:
            self._done = True
            self.log.debug("[%04d][%03d] work done %f"%(self.id,self.invoke_times,time.time()))
        """

def test():
    import vavava.util
    from vavava.util import _interval_timer
    log = vavava.util.initlog("./log/test_dispatcher.log")

    #from spiders.track_gripper import TrackGripperWork
    from vavava.workshop import WorkShop
    ws = WorkShop(log=log)
    #ws.StartWork()

    dispatcher = Dispatcher({"test":ws})

    dispatcher.ActivateAllWorkshops()

    index=0
    try:
        for i in range(1):
            tgw = TWork(index,period=1800,name="test_work")
            dispatcher.AddWork(work=tgw)
            index += 1

        while True:
            time.sleep(1)

        print('main thread(%f):stop'%_interval_timer())
        dispatcher.StopWork()
        print('main thread(%f):stopped'%_interval_timer())
    except(KeyboardInterrupt):
        print('main thread(%f): User canceled by Ctrl-c'%_interval_timer())
    finally:
        print('main thread(%f):stop'%_interval_timer())
        dispatcher.StopWork()
        print('main thread(%f):stopped'%_interval_timer())



if __name__ == '__main__':
    test()




"""



