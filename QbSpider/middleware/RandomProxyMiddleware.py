#!/usr/bin/python
# -*-coding:utf-8-*-
import os,sys
import logging
logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.abspath("../../"))
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from scrapy.xlib.tx import ResponseFailed
from scrapy.exceptions import IgnoreRequest
from scrapy.core.downloader.handlers.http11 import TunnelError
import random
import pymysql

class ProxyMiddleware(object):
    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError, ResponseFailed,
                           IOError,TunnelError)

    def __init__(self, settings):
        self.settings = settings
        # self.proxys = ['localhost']
        self.proxys = []
        self.index = 0
        # self.lastTime = 0
        self.retryurl = {}

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def fetch_new_proxyes(self):
        # try:
        #     self.proxys.remove("localhost")
        # except Exception, e:
        #     pass
        mysqlset = self.settings.getdict("PROXY_MYSQL")
        conn = pymysql.connect(
            host=mysqlset['Host'],
            user=mysqlset['User'],
            passwd=mysqlset['Passwd'],
            db=mysqlset['Db'],
            charset=mysqlset['Charset']
        )
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(self.settings.get("PROXY_SQL"))
        for r in cur:
            ips = "http://" + r['ip']
            if ips not in self.proxys:
                self.proxys.append(ips)
        cur.close()
        conn.close()
        #self.lastTime = time.time()

    def RetryStatus(self, url):
        if not self.retryurl.has_key(url):
             self.retryurl[url] = 0
        else:
            self.retryurl[url] += 1
        if self.retryurl[url] < self.settings.get("RETRY_TIMES", 3):
            return True
        return False

    def process_request(self, request, spider):

        if "://" not in request.url:
            raise IgnoreRequest

        login_url = self.settings.get("LOGIN_URL", "")
        if request.url in login_url:
            self.proxys = []
            logger.debug("url=======================%s##############fetch_new_proxyes", request.url)
            self.fetch_new_proxyes()

        if len(self.proxys) < self.settings.get("PROXY_MIN_NUM", 10):
            self.fetch_new_proxyes()

        if spider.settings.get("USEPROXYHIGHLEVEL") is False:
            # if (len(self.proxyes) > 1):
            #     self.index = (self.index + 1) % len(self.proxyes)
            # else:
            #     self.index = 0
            #logger.debug("USEPROXYHIGHLEVEL=%s------------------------------", spider.settings.get("USEPROXYHIGHLEVEL"))
            if "proxy" not in request.meta.keys():
                proxy = self.proxys[0]
                if proxy != 'localhost':
                    request.meta["proxy"] = proxy
                else:
                    request.meta.pop("proxy", None)
        else:
            # if self.index == 0:
            #     try:
            #         self.proxys.remove("localhost")
            #     except Exception,e:
            #         pass
            #         #logging.warning(msg=e.message)
            # self.index+=1
            proxy = random.choice(self.proxys)
            request.meta["proxy"] = proxy
            # logger.debug("proxy>>>>>>>>>>>>>>>>===========%s",proxy)

    def process_response(self, request, response, spider):
        spider.logger.debug("proxy<%s> retry<%s>times response.status<%s> request.url<%s>" % (request.meta.get('proxy', ''), self.retryurl.get(request.url,""),response.status, request.url))
        #if not self.settings.get("REDIRECT_ENABLED"):
        if not self.settings.get("REDIRECT_ENABLED") and self.settings.get("LOGIN_TYPE") is False:
            retry_http_code = self.settings.getlist("RETRY_HTTP_CODES") + [302, 301]
        else:
            retry_http_code = self.settings.get("RETRY_HTTP_CODES")

        # spider.logger.debug("self.settings.get(REDIRECT_ENABLED)===============<%s> " % self.settings.get("REDIRECT_ENABLED"))
        # spider.logger.debug("self.settings.get(LOGIN_TYPE)===============<%s> " % self.settings.get("LOGIN_TYPE"))
        # spider.logger.debug("retry_http_code===============<%s> " % retry_http_code)
        if response.status != 200 and response.status in retry_http_code:
            try:
                if request.meta.get('proxy', False):
                    self.proxys.remove(request.meta.get('proxy'))
                else:
                    self.proxys.remove("localhost")
            except Exception,e:
                # logging.warning(msg=e.message)
                pass

            if self.RetryStatus(request.url):
                new_request = request.copy()
                new_request.dont_filter = True
                if len(self.proxys) < self.settings.get("PROXY_MIN_NUM", 10):
                    self.fetch_new_proxyes()
                proxy = random.choice(self.proxys)
                new_request.meta["proxy"] = proxy
                return new_request
            else:
                logging.warning("%s retry<%s> %s ignore"%(spider.name,self.retryurl[request.url],request.url))
                raise IgnoreRequest
        else:
            if self.retryurl.has_key(request.url):
                self.retryurl.pop(request.url, None)
            return response

    def process_exception(self, request, exception, spider):
        #spider.logger.debug("%s %s %s" % (request.meta.get('proxy', ''), exception.message, request.url))
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY):
            try:
                if request.meta.get('proxy', False):
                    self.proxys.remove(request.meta.get('proxy'))
                else:
                    self.proxys.remove("localhost")
            except Exception, e:
                pass
                #logging.warning(msg=e.message)

            #if self.RetryStatus(request.url):
            new_request = request.copy()
            new_request.dont_filter = True
            if len(self.proxys) < self.settings.get("PROXY_MIN_NUM", 10):
                self.fetch_new_proxyes()
            proxy = random.choice(self.proxys)
            new_request.meta["proxy"] = proxy
            return new_request
            # else:
            #     raise IgnoreRequest


class ProxyMiddleware_VPS(object):
    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError, ResponseFailed,
                           IOError,TunnelError)

    def __init__(self, settings):
        self.settings = settings
        self.proxys = ['localhost']
        self.index = 0
        # self.lastTime = 0
        self.retryurl = {}

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def fetch_new_proxyes(self):
        mysqlset = self.settings.getdict("PROXY_MYSQL_VPS")
        conn = pymysql.connect(
            host=mysqlset['Host'],
            user=mysqlset['User'],
            passwd=mysqlset['Passwd'],
            db=mysqlset['Db'],
            charset=mysqlset['Charset']
        )
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(self.settings.get("PROXY_SQL_VPS"))
        for r in cur:
            ips = "http://" + r['ip']
            if ips not in self.proxys:
                print ips
                self.proxys.append(ips)
        cur.close()
        conn.close()
        #self.lastTime = time.time()

    def RetryStatus(self,url):
        if not self.retryurl.has_key(url):
             self.retryurl[url]=0
        else:
            self.retryurl[url]+=1
        if self.retryurl[url]<self.settings.get("RETRY_TIMES_VPS", 3):
            return True
        return False

    def process_request(self, request, spider):

        if "://" not in request.url:
            raise IgnoreRequest

        login_url = self.settings.get("LOGIN_URL", "")
        if request.url in login_url:
            self.proxys = ['localhost']
            self.fetch_new_proxyes()

        if len(self.proxys) < self.settings.get("PROXY_MIN_NUM_VPS", 2):
            self.fetch_new_proxyes()

        if spider.settings.get("USEPROXYHIGHLEVEL") is False:
            # if (len(self.proxyes) > 1):
            #     self.index = (self.index + 1) % len(self.proxyes)
            # else:
            #     self.index = 0
            if "proxy" not in request.meta.keys():
                proxy=self.proxys[0]
                if proxy!='localhost':
                    request.meta["proxy"] = proxy
                else:
                    request.meta.pop("proxy",None)
        else:
            # if self.index == 0:
            #     try:
            #         self.proxys.remove("localhost")
            #     except Exception,e:
            #         pass
            #         #logging.warning(msg=e.message)
            # self.index+=1
            proxy = self.proxys[-1]
            request.meta["proxy"] = proxy

    def process_response(self, request, response, spider):
        spider.logger.debug("proxy<%s> retry<%s>times response.status<%s> request.url<%s>" % (request.meta.get('proxy', ''), self.retryurl.get(request.url,""),response.status, request.url))
        #if not self.settings.get("REDIRECT_ENABLED"):
        if not self.settings.get("REDIRECT_ENABLED") and self.settings.get("LOGIN_TYPE") is False:
            retry_http_code = self.settings.getlist("RETRY_HTTP_CODES") + [302,301]
        else:
            retry_http_code = self.settings.get("RETRY_HTTP_CODES")

        if response.status != 200 and response.status in retry_http_code:
            try:
                if request.meta.get('proxy', False):
                    self.proxys.remove(request.meta.get('proxy'))
                else:
                    self.proxys.remove("localhost")
            except Exception,e:
                #logging.warning(msg=e.message)
                pass
            if self.RetryStatus(request.url):
                new_request = request.copy()
                new_request.dont_filter = True
                if len(self.proxys) < self.settings.get("PROXY_MIN_NUM_VPS", 2):
                    self.fetch_new_proxyes()
                # proxy = random.choice(self.proxys)
                proxy = self.proxys[-1]
                new_request.meta["proxy"] = proxy
                return new_request
            else:
                logging.warning("%s retry<%s> %s ignore"%(spider.name,self.retryurl[request.url],request.url))
                raise IgnoreRequest
        else:
            if self.retryurl.has_key(request.url):
                self.retryurl.pop(request.url, None)
            return response

    def process_exception(self, request, exception, spider):
        #spider.logger.debug("%s %s %s" % (request.meta.get('proxy', ''), exception.message, request.url))
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY):
            try:
                if request.meta.get('proxy', False):
                    self.proxys.remove(request.meta.get('proxy'))
                else:
                    self.proxys.remove("localhost")
            except Exception,e:
                #logging.warning(msg=e.message)
                pass
            #if self.RetryStatus(request.url):
            new_request = request.copy()
            new_request.dont_filter = True
            if len(self.proxys) < self.settings.get("PROXY_MIN_NUM_VPS", 2):
                self.fetch_new_proxyes()
            proxy = self.proxys[-1]#random.choice(self.proxys)
            new_request.meta["proxy"] = proxy
            return new_request
            # else:
            #     raise IgnoreRequest

