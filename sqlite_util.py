#! /usr/bin/env python
# -*- coding: utf-8 -*-


import time
import Queue
import sqlite3
import threading
from vavava import util


class DBBase:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_connection(self):
        self.conn = sqlite3.connect(self.db_path, timeout=3)

    def excute(self, sql):
        self.conn.execute(sql)

class WorkBase:
    def handle(self, db):
        raise r"uncomplete implament"

class dbpool(threading.Thread):
    def __init__(self, path, cls=DBBase):
        threading.Thread.__init__(self)
        self.daemon = True
        self.db = None
        self.path = path
        self.cls = cls
        self.que = Queue.Queue()
        self.ev = threading.Event()
        self.start()

    def queue_work(self, work):
        self.que.put(work)

    def run(self):
        self.db = self.cls(self.path)
        while not self.ev.isSet():
            dbop = self.que.get(timeout=3)
            if dbop:
                dbop.handle(self.db)

    def stop(self):
        self.ev.set()

if __name__ == "__main__":
    import time
    class testwork(WorkBase):
        def __init__(self):
            self.name = 'aaa'
        def handle(self):
            print 'yes ', self.name
    pool = dbpool(None)
    for i in range(10):
        pool.queue_work(testwork())
        time.sleep(1)
