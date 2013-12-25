#!/usr/bin/env python
# coding=utf-8

import os
import sys
import errno


def walk(top, topdown=True, onerror=None, followlinks=False):
    isfile, islink, join, isdir = os.path.isfile, os.path.islink, os.path.join, os.path.isdir
    try:
        names = os.listdir(top)
    except os.error, os.err:
        if onerror is not None:
            onerror(err)
        return

    dirs, files, dlns, flns, others = [], [], [], [], []
    for name in names:
        fullname = join(top, name)
        print "==", fullname
        if isdir(fullname):
            print "dir ", fullname
            if islink(fullname):
                print "linked ", fullname
                dlns.append(name)
            else:
                dirs.append(name)
        elif isfile(fullname):
            print "file ", fullname
            if islink(fullname):
                flns.append(name)
            else:
                files.append(name)
        else:
            print "other ", fullname
            others.append(name)

    if topdown:
        yield top, dirs, files, dlns, flns, others

    if followlinks is True:
        for dlink in dlns:
            for x in walk(join(top, dlink), topdown, onerror, followlinks):
                yield x

    if not topdown:
        yield top, dirs, files, dlns, flns, others

for tmp in walk(top="/Users/pk/lib", followlinks=True):
    print tmp

# for tmp in os.walk(top="/Users/pk/lib", followlinks=False):
#     print tmp


