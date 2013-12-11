#!/usr/bin/env python
# coding=utf-8

import re
import os.path
import time

get_time_string = lambda : time.strftime("%Y%m%d%H%M%S", time.localtime())


import signal
class SignalHandler:
    """handle SIGTERM signal for current process """
    def __init__(self, sig=signal.SIGTERM, callback=None):
        self.handle = self._handle
        self.callback = callback
        signal.signal(sig, self.handle)

    def _handle(self, signum, frame):
        if signum is signal.SIGTERM:
            if self.callback:
                self.callback()
            else:
                exit(0)

def assure_path(path):
    if not os.path.isdir(path):
        os.makedirs(path)

import logging
def get_logger(logfile=None, level=logging.DEBUG):
    logger = logging.getLogger()
    if logfile:
        hdlr = logging.FileHandler(logfile)
        hdlr.setLevel(level=level)
        formatter = logging.Formatter("%(asctime)s[%(levelname)s]%(message)s")
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
    console = logging.StreamHandler()
    console.setLevel(level)
    formatter = logging.Formatter("%(asctime)s[%(levelname)s]%(message)s")
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger.setLevel(level)
    return logger

import threading
class SynDict(object):
    """
    a syn dict
    """
    from threading import Lock
    def __init__(self):
        self._dict = {}
        self._mt = threading.Lock()
    def add(self,k,v):
        self._mt.acquire()
        self._dict[k]=v
        self._mt.release()
    def popitem(self):
        v = None
        self._mt.acquire()
        if len(self._dict) > 0:
            k,v = self._dict.popitem()
        self._mt.release()
        return v

def reg_helper(text, reg_str="", mode=re.I|re.S):
    reg = re.compile(reg_str,mode)
    return reg.findall(text)

def importAny(name):
    try:
        return __import__(name, fromlist=[''])
    except:
        try:
            i = name.rfind('.')
            mod = __import__(name[:i], fromlist=[''])
            return getattr(mod, name[i+1:])
        except:
            raise RuntimeError('No module of: %s found'%(name))

def get_sufix(name):
    return os.path.splitext(name)[1][1:]

def copy_dir(sourceDir, targetDir, types={}):
    sourceDir = os.path.abspath(sourceDir)
    targetDir = os.path.abspath(targetDir)
    for f in os.listdir(sourceDir):
        sourceF = os.path.join(sourceDir, f)
        targetF = os.path.join(targetDir, f)
        if os.path.isfile(sourceF):
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            if types.has_key(get_sufix(f)):
                open(targetF, "wb").write(open(sourceF, "rb").read())
        if os.path.isdir(sourceF):
            copy_dir( sourceF, targetF, types )

def readfile(name):
    fullname = os.path.abspath(name)
    path = os.path.split(fullname)[0]
    if not os.path.isdir(path):
        os.makedirs(path)
    return open(name, "r").readlines()


