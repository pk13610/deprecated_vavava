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
    def handle(self):
        raise r"uncomplete implament"

class dbpool:
    def __init__(self, path, cls=DBBase):
        self.db = None
        self.path = path
        self.cls = cls
        self.que = Queue.Queue()
        self.ev = threading.Event()

    def queue_work(self, work):
        self.que.put(work)

    def _runnable(self):
        self.db = self.cls(self.path)
        while self.ev.isSet():
            dbop = self.que.get(timeout=3)
            if dbop:
                dbop.handle()

    def run(self):
        self.th = threading.Thread(target=self._runnable())
        self.th.daemon = True
        self.ev.clear()
        self.th.start()

    def stop(self):
        if self.th:
            self.ev.set()
            self.th.join(30)
