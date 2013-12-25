#!/usr/bin/env python
# coding=utf-8

import re
import sys
import os.path
import time
import chardet

get_time_string = lambda : time.strftime("%Y%m%d%H%M%S", time.localtime())
get_charset = lambda ss: chardet.detect(ss)['encoding']
set_default_utf8 = lambda : reload(sys).setdefaultencoding("utf8")
get_file_sufix = lambda name: os.path.splitext(name)[1][1:]

import signal
class SignalHandlerBase:
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
def get_logger(logfile=None, stream=sys.stdout, level=logging.DEBUG):
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

import json
class JsonConfig:
    def __init__(self, path=None, attrs=[]):
        for attr in attrs:
            setattr(self, attr, None)
        if path:
            for k, v in json.load(open(path)).items():
                setattr(self, k, v)

def reg_helper(text, reg_str="", mode=re.I|re.S):
    reg = re.compile(reg_str,mode)
    return reg.findall(text)

def importAny(name):
    """ import module at any place """
    try:
        return __import__(name, fromlist=[''])
    except:
        try:
            i = name.rfind('.')
            mod = __import__(name[:i], fromlist=[''])
            return getattr(mod, name[i+1:])
        except:
            raise RuntimeError('No module of: %s found'%(name))

def copy_dir(sourceDir, targetDir, types={}):
    sourceDir = os.path.abspath(sourceDir)
    targetDir = os.path.abspath(targetDir)
    for f in os.listdir(sourceDir):
        sourceF = os.path.join(sourceDir, f)
        targetF = os.path.join(targetDir, f)
        if os.path.isfile(sourceF):
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            if types.has_key(get_file_sufix(f)):
                open(targetF, "wb").write(open(sourceF, "rb").read())
        if os.path.isdir(sourceF):
            copy_dir( sourceF, targetF, types )

def readfile(name):
    fullname = os.path.abspath(name)
    path = os.path.split(fullname)[0]
    if not os.path.isdir(path):
        os.makedirs(path)
    return open(name, "r").readlines()

def asure_path(path):
    if not os.path.isdir(path):
        asure_path(os.path.dirname(path))
        os.mkdir(path)

def walk(top, topdown=True, onerror=None, followlinks=False):
    """
    os.walk() ==> top, dirs, nondirs
    walk() ==> top, dirs, files, dirlinks, filelinks, others
    """
    isfile, islink, join, isdir = os.path.isfile, os.path.islink, os.path.join, os.path.isdir
    try:
        names = os.listdir(top)
    except os.error, os.err:
        if onerror is not None:
            onerror(os.err)
        return

    dirs, files, dlns, flns, others = [], [], [], [], []
    for name in names:
        fullname = join(top, name)
        if isdir(fullname):
            if islink(fullname):
                dlns.append(name)
            else:
                dirs.append(name)
        elif isfile(fullname):
            if islink(fullname):
                flns.append(name)
            else:
                files.append(name)
        else:
            others.append(name)

    if topdown:
        yield top, dirs, files, dlns, flns, others

    for name in dirs:
        for x in walk(join(top, name), topdown, onerror, followlinks):
            yield x

    if followlinks is True:
        for dlink in dlns:
            for x in walk(join(top, dlink), topdown, onerror, followlinks):
                yield x

    if not topdown:
        yield top, dirs, files, dlns, flns, others
