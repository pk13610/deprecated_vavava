#!/usr/bin/env python
# coding=utf-8

import httputil
from lxml import etree

class SpiderUtil:
    @staticmethod
    def get_tags(url, xpath, attribs):

        data = []
        html = httputil.HttpUtil().get(url)
        for tag in etree.HTML(html).xpath(xpath):
            for attrib in attribs:
                if tag.attrib.has_key(attrib):
                    data.append(tag.attrib[attrib])
                    break
        return data

if __name__ == "__main__":
    for data in SpiderUtil.get_tags(
        r'http://www.baidu.com',
        r'/html/head/meta',
        [r'content']
    ):
        print data
