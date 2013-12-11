#!/usr/bin/env python
# coding:utf-8

import sys
import os

def ensure_utf8():
    print 'current encoding is ', sys.getdefaultencoding()
    reload(sys).setdefaultencoding("utf8")

def is_in_path(file_path):    
    file_path = os.path.abspath(file_path)
    if os.path.isfile(file_path):
        file_path = os.path.dirname(file_path)
    if not file_path.endswith('/'):
        file_path += '/'
    thispath=sys.path
    pathmap={}
    for p in thispath:
        op = os.path.abspath(p)
        if not op.endswith('/'):
            op += '/'
        if op == file_path:
            print file_path
            return
    print "NO"

def check(arg):
    if arg == 'path':
        for p in sys.path:
            print p
    elif arg.endswith('/'):
        is_in_path(arg)
    else:
        exec('import ' + arg)
        exec('print ' + arg + ".__file__")

if __name__ == "__main__":
    check(sys.argv[1])
