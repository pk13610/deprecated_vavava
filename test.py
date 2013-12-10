#!/usr/bin/env python
# coding=utf-8

import httputil
import util
import time
import re

# print time.strptime(u"2013-11-22 10:01 PM".strip()[0: 16], "%Y-%m-%d %H:%M")

post = 'ss2012--11--3@12:1 123'
# DBRowUrl(title='title', url='url',
#          post_time=post, category=0)
# tt = re.compile(r"(?P<tt>\d{2-4}[--|-]\d{1,2}[--|-]\d{1,2}(\s|@)\d{1,2}:\d{1,2})")
tt = re.compile(r"(?P<tt>\d{4}(--|-)\d{1,2}(--|-)\d{1,2}(\s|@)\d{1,2}:\d{1,2})")
mm = tt.findall(post)[0].replace('--', '-').replace('@', ' ')
print mm
