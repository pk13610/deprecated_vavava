#!/usr/bin/env python
# coding=utf-8
#-------------------------------------------------------------------------------
# Name:        模块1
# Purpose:
#
# Author:      vavava
#
# Created:     05/11/2012
# Copyright:   (c) vavava 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------

class OBase(object):
    def __init__(self,name):
        self._name = name

    def getName(self):
        return self._name

    def setName(self,name):
        self._name = name

