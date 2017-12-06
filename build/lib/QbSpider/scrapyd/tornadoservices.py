# coding=utf-8
#!/usr/bin/env python
import sys,os
sys.path.append(os.path.abspath("../../"))
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import urllib, uuid
import requests
import json
from twisted.internet import reactor
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from QbSpider.utils.RedisUtil import RedisConfUtil as rcu

con = rcu().get_redis()
from QbSpider.spiders.jd_spider import JdSpider
import logging

spider_cls = {"jingdong": JdSpider()}


class MainHandler(tornado.web.RequestHandler):

    def delaycrawl(self, pay_load):

        try:

            requests.post("http://localhost:10010/schedule.json", data=pay_load)

        except Exception, e:

            logging.warning(msg=e.message)

            return {"error": "spider scheduler error"}

        return {"status":0,"jobid": pay_load["jobid"]}

    def realtimecrawl(self, pay_load):

        settings = get_project_settings()

        setting = {}

        setting.update({y[:y.index("=")]: y[y.index("=") + 1:] for y in [i for i in pay_load["setting"]]})

        for k, v in setting.iteritems():
            settings.set(k, v)

        runner = CrawlerProcess(settings)

        d = runner.crawl(spider_cls[pay_load["spider"]])

        d.addBoth(lambda _: reactor.stop())

        reactor.run()

        jobid = pay_load["jobid"]

        status = con.hmget(jobid, "status")

        return {"status": status[0],"jobid":jobid}

    def check_contain_chinese(self, check_strs):

        for ch in check_strs.decode('utf-8'):

            if u'\u4e00' <= ch <= u'\u9fff':
                return True

        return False

    def get(self):
        print self.request
        argss = dict((k, v[0]) for k, v in self.request.query_arguments.iteritems())
        spider_name = argss.get("spider", None)
        logintype = argss.get("logintype",None)
        if logintype not in [1,2,"1","2"]:
            self.write({"error": "logintype must be 1 or 2"})
            return
        else:
            logintype = int(logintype)
        if not spider_name:
            self.write({"error": "spidername is None"})
            return
        if not argss.get("spidertype", None):
            self.write({"error": "spidertype is None"})
            return
        else:
            if "delay" == argss.get("spidertype", None):
                flag = False
            elif "realtime" == argss.get("spidertype", None):
                flag = True
            else:
                self.write({"error": "spidertype must be delay or realtime"})
                return
        argg = []
        for i in xrange(len(argss.keys())):
            if argss.keys()[i] != "spider":
                # if self.check_contain_chinese(argss[argss.keys()[i]]):
                argg.append(argss.keys()[i].upper() + "=%s" % urllib.quote(argss[argss.keys()[i]]))
                # else:
                #     argg.append(argss.keys()[i].upper() + "=%s" % argss[argss.keys()[i]])
        jobid = uuid.uuid1().hex
        argg.append("JOBID=%s" % urllib.quote(jobid))
        setting = tuple(argg)
        pay_load = {"project": "QbSpider", "spider": spider_name, "jobid": jobid, "setting": setting}
        if not flag and logintype == 1:
            self.write(self.delaycrawl(pay_load))
            return
        elif flag and logintype == 2 :
            msg = self.realtimecrawl(pay_load)
            self.write(msg)
            if msg["status"] == "1":
                p_l = list(pay_load["setting"])
                [p_l.remove(s) for s in p_l if "SPIDERTYPE" in s]
                p_l.append("SPIDERTYPE=%s"%urllib.quote("delay"))
                pay_load.update({"setting":p_l})
                print "0"*66
                print pay_load
                self.delaycrawl(pay_load)

                return
            return
        else:
            self.write({"error":"spidertype not match logintype"})

class App(object):

    def make_app(self):
        return tornado.web.Application([
            (r"/schedule", MainHandler),
        ])


class StartServices(object):
    app = App().make_app()
    sockets = tornado.netutil.bind_sockets(9999)
    tornado.process.fork_processes(0)
    server = HTTPServer(app)
    server.add_sockets(sockets)
    IOLoop.current().start()


if __name__ == "__main__":

    StartServices()
