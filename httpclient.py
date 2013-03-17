#!/usr/bin/env python
# coding=utf-8

if __name__ == '__main__':
    """ for file debug"""
    import sys,os
    sys.path.insert(0,os.path.join( os.getcwd(), '..' ))

import urllib,urllib2,socket
from cookielib import LWPCookieJar
from vavava.util import  LogAdapter
from gzip import GzipFile
from io import BytesIO

class HttpClient(object):
    """ a simple client of http"""
    def __init__(self,log=None,debug_level=1,req_timeout=30):
        self.__log = LogAdapter(log)
        self.__content = None
        self.__cookie = None
        self.__cookie_str = ""
        self.__req_timeout = req_timeout
        self.__httpDebugLevel = debug_level
        self.__headers_dic = {'Referer':"http://www.google.com/"}
        self.__cookie_enabled = False
        self.__proxy_enable = False
        self.__proxy_dic = None
        self._opener = None
        self.__buffer_size = 1024*100
        self.SetDebugLevel(debug_level)
        self.header_refer_ = "http://www.google.com/"
        self.header_user_agent_ = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
    def __del__(self):
        print "delete"
    def Get(self,url,callback=None):
        if self._opener is None:
            self.__install_opener()
        self.__init_header(url)
        socket.setdefaulttimeout(self.__req_timeout)
        req = urllib2.Request(url,headers=self.__headers_dic)
        resp = self._opener.open(req,timeout=self.__req_timeout)
        if callback:
            data = resp.read(self.__buffer_size)
            while data:
                if not callback.write(data):
                    return
                data = resp.read(self.__buffer_size)
        else:
            self.__content = resp.read()
            return self.__content
    def Post(self,url,post_dic):
        if self._opener is None:
            self.__install_opener()
        postdata=urllib.urlencode(post_dic).encode('gb2312')
        self.__init_header(url)
        socket.setdefaulttimeout(self.__req_timeout)
        req = urllib2.Request(url,data=postdata,headers=self.__headers_dic)
        resp = self._opener.open(req)
        self.__content = resp.read(self.__buffer_size)
        return self.__content
    def EnableCookieSupport(self,enable=True):
        if enable and self.__cookie is None:
            self.__cookie = LWPCookieJar()
        else:
            self.__cookie = None
        self.__cookie_enabled = enable
        self.__install_opener()
    def AddHeader(self,kw={}):
        for k in kw:
            self.__headers_dic[k] = kw[k]
    def AddProxy(self,proxy_pair):
        self.__proxy_dic = proxy_pair
        self.__proxy_enable = True
        self.__install_opener()
    def SetDebugLevel(self,level=0):
        from httplib import HTTPConnection
        HTTPConnection.debuglevel = level
        self.__httpDebugLevel=level
    def __install_opener(self):
        if self._opener is None:
            self._opener = urllib2.build_opener(
                ContentEncodingProcessor() ) # always support zlib
        if self.__cookie_enabled:
            self._opener.add_handler(
                urllib2.HTTPCookieProcessor(self.__cookie) )
        if self.__proxy_enable:
            self._opener.add_handler(
                urllib2.ProxyHandler(self.__proxy_dic) )
        urllib2.install_opener(self._opener)
    def __init_header(self,url):
        #self.__headers_dic = {'Referer':url}
        if self.header_user_agent_  is not None:
            self.__headers_dic['Referer'] = self.header_refer_
        if self.header_user_agent_ is not None:
            self.__headers_dic['User-Agent'] = self.header_user_agent_
        if False and self.__cookie_enabled:
            self.__cookie_str=""
            for s in self.__cookie:
                self.__cookie_str += ";" + s
            if self.__cookie_str.strip() != "":
                self.__headers_dic['Set-Cookie'] = self.__cookie_str
        return self.__headers_dic
#######################ContentEncodingProcessor#################################
# copy from http://www.pythonclub.org/python-network-application/observer-spider
import zlib
class ContentEncodingProcessor(urllib2.BaseHandler):
  """A handler to add gzip capabilities to urllib2 requests """
  # add headers to requests
  def http_request(self, req):
    req.add_header("Accept-Encoding", "gzip, deflate")
    return req
  # decode
  def http_response(self, req, resp):
    old_resp = resp
    # gzip
    if resp.headers.get("content-encoding") == "gzip":
        gz = GzipFile( fileobj=BytesIO(resp.read()), mode="r" )
        resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)
        resp.msg = old_resp.msg
    # deflate
    if resp.headers.get("content-encoding") == "deflate":
        gz = BytesIO( deflate(resp.read()) )
        resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)  # 'class to add info() and
        resp.msg = old_resp.msg
    return resp
# deflate support
def deflate(data):   # zlib only provides the zlib compress format, not the deflate format;
  try:               # so on top of all there's this workaround:
    return zlib.decompress(data, -zlib.MAX_WBITS)
  except zlib.error:
    return zlib.decompress(data)
#######################ContentEncodingProcessor#################################

# test code  ########################################################################
def test_get():
    url = r'http://www.cqent.net/index.php'
    client = HttpClient()
    client.AddProxy({"http":"http://127.0.0.1:8087"})
    content=client.Get(url)
    print( content.decode('utf8'))

def test_post():
    url = r'http://www.cqent.net/index.php?s=vod-search'
    postdata = {
        '__ppvod__' :'3133627a8f406588b41c90d5d15c7fad',
        'id'	    :'abc',
        'submit'    :'asdfasdf',
        'x'	        :'name'
    }
    client = HttpClient()
    content=client.Post(url,postdata)
    print( content.decode('utf8'))


class HttpClientTest(object):
    """ a simple client of http"""
    def __init__(self,log=None):
        self.log = LogAdapter(log)

    def __del__(self):
        print "delete"

    def Get(self,url):
        #opener = urllib2.build_opener( ContentEncodingProcessor() )
        req = urllib2.Request(url)
        resp = urllib2.urlopen(req,timeout=33)
        content = resp.read()
        resp.close()
        return len(content)

import time
def test4():
    while True:
        h=HttpClientTest()
        h.log.info(h.Get("http://www.baidu.com"))
        time.sleep(0.01)

if __name__ == '__main__':
    import vavava.util
    log = vavava.util.initlog("./log/test_http.log")
    try:
        test4()
    except(KeyboardInterrupt):
        log.info('main thread(%f):stop',time.clock())
        a=raw_input()
        log.info('main thread(%f):stopped',time.clock())

