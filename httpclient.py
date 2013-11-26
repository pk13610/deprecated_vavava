#!/usr/bin/env python
# coding=utf-8

#if __name__ == '__main__':
#    """ for file debug"""
#    import sys,os
#    sys.path.insert(0,os.path.join( os.getcwd(), '..' ))

import urllib
import urllib2
import socket
from cookielib import LWPCookieJar
from gzip import GzipFile
from io import BytesIO
import vavava

DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
DEFAULT_REFERER = "http://www.google.com/"
DEFAULT_BUFFER_SIZE = 1024*100
DEFAULT_CHARSET = "utf8"
DEFAULT_TIMEOUT = 30 #MS
DEFAULT_DEBUG_LVL = 0

class HttpClient(object):
    """ a simple client of http"""

    def __init__(self, debug_lvl=DEFAULT_DEBUG_LVL, req_timeout=DEFAULT_TIMEOUT, log=None):
        self._log = vavava.util.get_logger(log)
        self._cookie = None
        self._cookie_str = ""
        self._req_timeout = req_timeout
        self._httpDebugLevel = debug_lvl
        self._headers_dic = {}
        self._cookie_enabled = False
        self._proxy_enable = False
        self._proxy_dic = None
        self._opener = None
        self._is_busy = False
        self._buffer_size = DEFAULT_BUFFER_SIZE
        self._charset = DEFAULT_CHARSET
        self.SetDebugLevel(debug_lvl)
        self.header_refer_ = DEFAULT_REFERER
        self.header_user_agent_ = DEFAULT_USER_AGENT
        #self._content = None

    def Get(self,url):
        return self._request(url)

    def Post(self,url,post_dic):
        return self._request(url, post_data=urllib.urlencode(post_dic).encode(self._charset) )

    def FetchData(self, url, handler, post_data=None):
        data = self._request(url, post_data, handler)
        while data and handler and handler.handle(data):
            data = None
            data = self._request(url, post_data, handler)

    def EnableCookieSupport(self,enable=True):
        if enable and self._cookie is None:
            self._cookie = LWPCookieJar()
        else:
            self._cookie = None
        self._cookie_enabled = enable
        self._install_opener()

    def AddHeader(self,kw={}):
        for k in kw:
            self._headers_dic[k] = kw[k]

    def AddHeaderRow(self, key, value):
        self._headers_dic[key] = value

    def AddProxy(self,proxy_pair):
        self._proxy_dic = proxy_pair
        self._proxy_enable = True
        self._install_opener()

    def SetDebugLevel(self,level=0):
        from httplib import HTTPConnection
        HTTPConnection.debuglevel = level
        self._httpDebugLevel=level

    def SetCharset(self, charset):
        self._charset = charset

    def _request(self, url, post_data=None, handler=None):
        if self._opener is None:
            self._install_opener()
        self._init_header(url)
        if handler and hasattr(handler, 'start'):
            self.AddHeaderRow('Content-Range', 'bytes %s-%s/%s' % (handler.start, handler.end, handler.len))
            self.AddHeaderRow('Content-Length', str(handler.len - handler.start))
        socket.setdefaulttimeout(self._req_timeout)
        req = urllib2.Request(url, data=post_data, headers=self._headers_dic)
        resp = self._opener.open(req)
        return resp.read(self._buffer_size)

    def _install_opener(self):
        if self._opener is None:
            self._opener = urllib2.build_opener(
                ContentEncodingProcessor() ) # always support zlib
        if self._cookie_enabled:
            self._opener.add_handler(
                urllib2.HTTPCookieProcessor(self._cookie) )
        if self._proxy_enable:
            self._opener.add_handler(
                urllib2.ProxyHandler(self._proxy_dic) )
        urllib2.install_opener(self._opener)

    def _init_header(self,url):
        if self.header_user_agent_  is not None:
            self._headers_dic['Referer'] = self.header_refer_
        if self.header_user_agent_ is not None:
            self._headers_dic['User-Agent'] = self.header_user_agent_
        if False and self._cookie_enabled:
            self._cookie_str=""
            for s in self._cookie:
                self._cookie_str += ";" + s
            if self._cookie_str.strip() != "":
                self._headers_dic['Set-Cookie'] = self._cookie_str
        return self._headers_dic

class DefaultDataHandler:
    """ fetch data and write to file """
    def __init__(self, name, mode="w"):
        self.fp = open(name, mode)

    def handle(self, data):
        self.fp.write(data)
        return True


    #######################ContentEncodingProcessor#################################
# copy from http://www.pythonclub.org/python-network-application/observer-spider
import zlib
class ContentEncodingProcessor(urllib2.BaseHandler):
    """A handler to add gzip capabilities to urllib2 requests """
    # add headers to requests

    def __init__(self):
        try:               # so on top of all there's this workaround:
            self.deflate = lambda data :zlib.decompress(data, -zlib.MAX_WBITS)
        except zlib.error:
            self.deflate = lambda data :zlib.decompress(data)

    def http_request(self, req):
        req.add_header("Accept-Encoding", "gzip,deflate")
        return req

    def http_response(self, req, resp):
        old_resp = resp
        # gzip
        if resp.headers.get("content-encoding") == "gzip":
            gz = GzipFile( fileobj=BytesIO(resp.read()), mode="r" )
            resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)
            resp.msg = old_resp.msg
            # deflate
        if resp.headers.get("content-encoding") == "deflate":
            gz = BytesIO( self.deflate(resp.read()) )
            resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)  # 'class to add info() and
            resp.msg = old_resp.msg
        return resp
#######################ContentEncodingProcessor#################################


def test_get():
    url = r'http://www.twitter.com'
    client = HttpClient()
    client.AddProxy({"http":"http://127.0.0.1:8087"})
    content=client.Get(url)
    print( content.decode('utf8'))

def test_post():
    url = r'http://www.2kdy.com/search.asp'
    post = {
        'searchword': r'lie'
    }
    client = HttpClient()
    client.SetCharset('gb2312')
    content=client.Post(url,post)
    print( content.decode('gbk'))

def test_fetch():
    url = r'http://pb.hd.sohu.com.cn/stats.gif?msg=caltime&vid=772959&tvid=596204&ua=pp&isHD=21&pid=348552429&uid=13832983422211404270&out=0&playListId=5029335&nid=353924663&tc=2400&type=vrs&cateid=&userid=&uuid=779b9c99-3c3a-52bc-2622-8bb0218cad5d&isp2p=0&catcode=101&systype=0&act=&st=144792%3B6560%3B143697%3B143699&ar=10&ye=2010&ag=5%u5C81%u4EE5%u4E0B&lb=2&xuid=&passport=&fver=201311211515&url=http%3A//tv.sohu.com/20120925/n353924663.shtml&lf=http%253A%252F%252Fv.baidu.com%252Fv%253Fword%253D%2525CA%2525AE%2525D2%2525BB%2525C2%2525DE%2525BA%2525BA%2526ct%253D301989888%2526rn%253D20%2526pn%253D0%2526db%253D0%2526s%253D0%2526fbl%253D800&autoplay=1&refer=http%3A//tv.sohu.com/20120925/n353924666.shtml&t=0.24127451563254'
    #url = r'http://211.161.44.71/youku/6976514083B4E8323E718325DF/0300010D00528A08445500054A57BFB54C329B-2C65-C560-C991-2ED7E5EEF980.flv'
    client = HttpClient()
    #client.AddProxy({"http":"http://127.0.0.1:8087"})
    handle = DefaultDataHandler('/Users/pk/Downloads/tmp.flv')
    client.FetchData(url,  handle)


if __name__ == '__main__':
    import time
    start = time.clock()
    try:
        test_fetch()
    except(KeyboardInterrupt):
        print '=====> test stop: run for %f min' % (time.clock()-start)
