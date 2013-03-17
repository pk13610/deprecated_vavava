#!/usr/bin/env python
# coding=utf-8

from vavava.util import LogAdapter
from MySQLdb import OperationalError

class _db_conn_helper:
    def __init__(self,conn=None,log=None):
        self.log = LogAdapter(log)
        self._conn = conn
        self._cursor = self._conn.cursor()

    def _handle_exception(self,e):
        """this error means that db conn or db internal
        err happened in the process of a transaction which
        can not be reconnect,try to reopen it manually
        """
        self.log.exception(e)
        if self._conn._transaction:
            self.log.error("db conn is dead,1111111111111.")
            self._conn._reset(True)
            self._cursor = self._conn.cursor()
        if not self._conn._ping_check():
            self.log.error("db conn is dead,reconnect failed.")

