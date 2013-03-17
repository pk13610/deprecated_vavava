#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
class GetIntervalTime:
    def start(self):
        self.start_time = time.clock()
    def getIntervalTime(self):
        return time.clock() - self.start_time
