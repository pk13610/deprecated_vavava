
import re,vavava.util
from vavava.httpclient import HttpClient
from vavava.util import LogAdapter
from time import localtime,time
import codecs,os

class Handler:
    def __init__(self,log,conn=None):
        self.log = log
        self.conn = conn

    def process(self):
        pass

class Fetcher:
    def __init__(self,item,debug_level=0,soc_timeout=10,log=None,name="<unknown>"):
        self._name = name
        self.log= LogAdapter(log=log)
        self._client = HttpClient(log,debug_level=debug_level,req_timeout=soc_timeout)
        self._client.timeout=11
        self._html = ""
        self.result_handlers = []
        self.exception_handler = []
        self.result = []

    def Fetch(self):
        try:
            self._fetch()
        except Exception as e:
            self.log.exception(e)
            self.handle_exception()
        self.handle_exception()

    def add_handler(self,handler=None,exception_handler=None):
        if exception_handler:
            self.exception_handlers.append(exception_handler)
        if handler:
            self.result_handlers.append(handler)

    def handle_result(self):
        for handler in self.result_handlers:
            handler.process()

    def handle_exception(self):
        for handler in self.exception_handler:
            handler.process()