#!/usr/bin/env python
# coding:utf-8

import sys, os

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

arg=sys.argv[1]

if arg == 'path':
    for p in sys.path:
        print p
elif arg.endswith('/'):
    is_in_path(arg)
else:
    exec('import ' + arg)
    exec('print ' + arg + ".__file__")
