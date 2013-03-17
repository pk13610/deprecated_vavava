#!/usr/bin/env python
# coding=utf-8
# Author:  vavava
# Created: 04/11/2012

if __name__ == '__main__':
    """ for file debug"""
    import sys,os
    sys.path.insert(0,os.path.join( os.getcwd(), '..' ))
from vavava.util import reg_helper,LogAdapter

class Fetcher(object):
    def __init__(self,log=None):
        self.filters = []
        self.log = LogAdapter(log)
        self.result_data_type = None
        self.datas = []

    def execute(self):
        for filter in self.filters:
            if filter[0] == 1:
                self.filter_get(filter[1],filter[2:])
            elif filter[0] == 2:
                self.filter_process(filter[1])
            elif filter[0] == 3:
                self.filter_result(filter[1:])
            elif filter[0] == 4:
                self.filter_result_db(filter[1],filter[2])

    def filter_get(self,charset="utf8",urls=[]):
        if len(urls) == 0:
            self.log.warn("no income resource")
        htmls = []
        for url in urls:
            try:
                from vavava.httpclient import HttpClient
                client=HttpClient(log=None,debug_level=0,req_timeout=30)
                data=client.Get(url)
                if data:
                    htmls.append(data.decode(charset))
                else:
                    self.log.debug(url)
            except Exception as e:
                self.log.LOG.exception(url,e)
        self.datas = htmls

    def filter_process(self,reg_str=""):
        result = []
        for data in self.datas:
            try:
                matches = reg_helper(data,reg_str)
                for match in matches:
                    result.append(match)
            except Exception as e:
                self.log.exception(e)
        self.datas = result

    def filter_result(self,keys=[]):
        class result_data:
            def __init__(self,values=[]):
                self.values = values

            def _key(self):
                key = ""
                for i in keys:
                    key += self.values[i]
                return key

            def __lt__(self, other):
                return self._key() < other._key()

            def __hash__(self):
                return hasattr(self._key())

        results = []
        for i in range(len(self.datas)):
            results.append( result_data(self.datas[i]) )
        self.datas = results

    def filter_result_db(self,conn,table,cols,values_format,types):
        if not (conn and table and cols and values_format):
            return
        sql = """
          insert into %s(%s)
          values(%s)
        """
        sql1= sql%(table,cols,values_format)
        tmp = []
        for result in self.results:
            for i in range(len(types)):
                tmp.append(self.data(types[i],result[i]))
            sql2 = sql1%tmp
            cursor = conn.cursor()
            cursor.execute(sql2)
            conn.commit()

    def data(self,t,data):
        if t == "string":
            return data
        elif t == "int":
            return int(data)
        elif t == "datetime":
            import time
            return time.strptime(data, "%d/%m/%y %H:%M")

if __name__ == "__main__":
    import vavava.util
    log = vavava.util.initlog("./log/fetcherpro.log")

    fetcher=Fetcher()
    fetcher.filters.append([1,'ISO-8859-1',"http://fastrackexpress.com.au/test.php?LIST=POST" ])
    fetcher.filters.append([2,r'<td>(?P<id>[^<]*)</td>'])
    fetcher.filters.append([3,0,1])
    fetcher.execute()

    fetch_format=r'http://auspost.com.au/track/track.html?id=%s'
    for item in fetcher.datas:
        log.debug("test:%s"%item.values)
        f = Fetcher(log)
        f.filters.append([1,"ISO-8859-1",fetch_format%item.values])
        f.filters.append([2,r'<\s*tr[^>]*>(?P<content>.*?)<\s*/\s*tr\s*>'])
        f.execute()
        if len(f.datas) > 0:
            log.info(item)
"""
    fetcher.filters.append(type=2,reg_str=r'<\s*tr[^>]*>(?P<content>.*?)<\s*/\s*tr\s*>')
    fetcher.filters.append(type=2,reg_str=r'<td[^>]*>(?P<content>.*?)(<span[^<]*?</span>)*</td>')
    fetcher.filters.append(
        type=3,
        table="tracking",
        cols="Name,TrackTime,Description,Location,Shipment_ID,Created,Modified",
        types=["string","datetime","string","string","int","datetime","datetime"]
        )
"""

