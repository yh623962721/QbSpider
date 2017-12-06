# coding=utf-8
import json
import logging
import time
import os
import urllib
import urllib2
from base64 import b64decode,b64encode
from os.path import join,dirname
import rsa
from Crypto.PublicKey import RSA
from scrapy.http import Request,FormRequest
from scrapy.selector.lxmlsel import HtmlXPathSelector
from scrapy.spiders import Spider
from scrapy.spider import CrawlSpider
from QbSpider.utils.utils import Util
from QbSpider.items import JdItem
import random
from scrapy import signals
from urlparse import urljoin
from QbSpider.utils.RedisUtil import RedisConfUtil as rcu
from QbSpider.scrapy_redis.queue import SpiderPriorityQueue
from QbSpider.scrapy_redis.spiders import RedisSpider
# import csv
# csvfile = file('csv_dazhongdianping.csv', 'wb')
# writer = csv.writer(csvfile)
# writer.writerow(["city", "type","title", "start", "review", "mean_price", "address", "address_2","taste","environment","service"])
import sys

reload(sys)
sys.setdefaultencoding("utf-8")


class dianpingSpider(CrawlSpider):

    name = "dianping"

    # BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    # BASE_DIR = os.path.abspath(__file__)
    #
    # print BASE_DIR

    # file_path = 'D:\work_python\QbSpider\QbSpider\project_test\citys.json'
    file_path = "/home/app_bank/task/QbSpider/QbSpider/spiders" + '/citys.json'
    json_dict = open(file_path, 'r')

    dict_json = json.loads(json_dict.read())

    json_dict.close()

    city_list = dict_json["city"]

    allowed_domains = []

    start_urls = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):

        spider = super(dianpingSpider, cls).from_crawler(crawler, *args, **kwargs)

        crawler.signals.connect(spider.spider_closed, signals.spider_closed)

        return spider

    def __init__(self, *a, **kw):

        super(dianpingSpider, self).__init__(*a, **kw)

        self.utils = Util()

        self.con = rcu().get_redis()

        self.con.ping()

        self.items = []
        self.city_id = []

    def start_requests(self):

        self.city_name = urllib.unquote(self.settings.get("CITY", None))

        self.vendor_name = urllib.unquote(self.settings.get("VENDOR", None))

        self.district_name = urllib.unquote(self.settings.get("DISTRICT", None))

        self.jobid = urllib.unquote(self.settings.get("JOBID", None))

        # print "[]"*99
        # print self.city_name, self.vendor_name, self.district_name, self.jobid
        # self.city_name = '北京'
        # self.vendor_name = '潇湘阁'
        # self.district_name = '朝阳区'
        # self.jobid = 'dianping_jobid'

        item = {"status": 0}

        self.items.append(item)

        self.con.hmset(self.jobid, item)
        # self.con.lpush(self.jobid, *self.items)

        if not self.city_name or not self.vendor_name or not self.jobid:

            logging.warning(msg="city_name or vendor_name or jobid is None")

            self.items[0]["status"] = 4  # 4代表传参错误

            return

        start_url = []

        start_url_meishi = []

        start_url_fenshu = []

        for city in self.city_list:

            if self.city_name in city:

                city_temp = city.split('|')

                url = 'http://www.dianping.com/search/keyword/%s/0_%s'% (city_temp[3], self.vendor_name)
                #美食的URL拼接
                url_meishi = "http://www.dianping.com/search/keyword/%s/10_%s"% (city_temp[3], self.district_name)
                #人气评分的URL拼接
                url_fenshu = "http://dpindex.dianping.com/ajax/suggest?keyword=%s&cityid=%s"% (self.vendor_name, city_temp[3])

                start_url.append(url)

                start_url_meishi.append(url_meishi)

                start_url_fenshu.append(url_fenshu)

                self.city_id.append(city_temp[3])

        for req_url_meishi in start_url_meishi:

            yield Request(req_url_meishi, callback=self.parse_district_num)

        for req_url_fenshu in start_url_fenshu:

            yield Request(req_url_fenshu, callback=self.parse_vendor_num)

        for req_url in start_url:

            yield Request(req_url, callback=self.parse)

    def parse(self, response):

        html = HtmlXPathSelector(response)

        if u"没有找到相应的商户" in "".join(html.xpath(u"//h4[contains(text(),'没有找到相应的商户')]/text()")):

            self.items[0]["status"] = 3   # 3代表没搜到商户

            logging.warning(msg="Did not find the corresponding merchant")

            return

        city_name = "".join(html.xpath("//a[@class='city J-city']/text()").extract())

        meta = {
            "city": city_name,
            "vendor_name": self.vendor_name,
            "district_name": self.district_name,
            "jobid": self.jobid,
            "base_url": "http://www.dianping.com",
            "type": ""
        }
        Effective_num = 0

        for items in html.xpath("//div[@id='shop-all-list']/ul/li"):

            title_name = "".join(items.xpath(".//div[@class='tit']/a/h4/text()").extract())

            if meta["vendor_name"] in title_name:

                Effective_num += 1

                title_url = "".join(items.xpath(".//div[@class='tit']/a[position()=1]/@href").extract())

                meta["type"] = "".join(items.xpath(".//div[@class='tag-addr']/a[position()=1]/span/text()").extract()).replace("\r","").replace("\n","").replace("\t","").replace(" ","")

                meta["business_district"] = "".join(items.xpath(".//div[@class='tag-addr']/a[position()=2]/span/text()").extract()).replace("\r","").replace("\n","").replace("\t","").replace(" ","")

                meta["url"] = urljoin(meta["base_url"], title_url)

                yield Request(urljoin(meta["base_url"], title_url), meta=meta, callback=self.parse_xiangxi)

        if Effective_num == 0:

            self.items[0]["status"] = 5  # 5代表搜索到商户，但不是指定的商户

            logging.warning(msg="Not a specified merchant")

            return

        next_page = "".join(html.xpath(u"//a[text()='下一页']/@href").extract())

        if next_page:

            yield Request(urljoin(meta["base_url"], next_page), callback=self.parse, meta=meta)

        del response

    def parse_district_num(self, response):

        html = HtmlXPathSelector(response)

        district_num = ''.join(html.xpath("//span[@class='num']/text()").extract()).replace("(", "").replace(")", "")

        item = {"district_num": district_num}

        self.con.hmset(self.jobid, item)

        del response

    def parse_vendor_num(self, response):

        hjson = json.loads(response.body.decode("utf-8"))

        for item_json in hjson["msg"]["records"]:

            if self.vendor_name in item_json["fullshopname"]:

                url = "http://dpindex.dianping.com/dpindex?shop=%s&type=index" % item_json["shopid"]

                meta = {
                    "shopid": item_json["shopid"],
                }
                yield Request(url, callback=self.parse_vendor_num_2, meta=meta)

        del response

    def parse_vendor_num_2(self, response):

        metas = response.meta

        for city_id in self.city_id:

            url_regionids = "http://dpindex.dianping.com/ajax/regionlist?cityid=%s&shopids=%s"% (city_id, metas["shopid"])

            yield Request(url_regionids, callback=self.parse_vendor_num_3, meta=metas)

    def parse_vendor_num_3(self, response):

        metas = response.meta

        html = response.body.decode("utf-8")

        try:

            hjson = json.loads(html)

            key = hjson["msg"]["regionids"][0]["key"]

            url_region_meishi = "http://dpindex.dianping.com/dpindex?category=10&region=%s&type=index&shop=%s" % (
            key, metas["shopid"])

            yield Request(url_region_meishi, callback=self.parse_renqizhishu)

        except:

            pass

    def parse_renqizhishu(self, response):

        html = HtmlXPathSelector(response)

        popularity_ranking = ''.join(html.xpath(u"//*[contains(text(),'第')]/text()").extract())

        item = {"popularity_ranking": popularity_ranking}

        self.con.hmset(self.jobid, item)

        del response

    def parse_xiangxi(self, response):

        html = HtmlXPathSelector(response)

        meta = response.meta

        meta["title"] = ''.join(html.xpath("//*[@id='basic-info']/h1/text()").extract()).replace("\r","").replace("\n","").replace("\t","").replace(" ","")

        meta["start"] = ''.join(html.xpath("//*[@id='basic-info']/div[1]/span[1]/@title").extract()).replace("\r","").replace("\n","").replace("\t","").replace(" ","")

        meta["mean_price"] = ''.join(html.xpath("//*[@id='basic-info']/div[1]/span[3]/text()").extract()).replace("\r","").replace("\n","").replace("\t","").replace(" ","")

        meta["address"] = ''.join(html.xpath("//*[@id='basic-info']/div[2]/span[2]/text()").extract()).replace("\r","").replace("\n","").replace("\t","").replace(" ","")

        meta["taste"] = ''.join(html.xpath("//*[@id='basic-info']/div[1]/span[4]/text()").extract()).replace("\r","").replace("\n","").replace("\t","").replace(" ","")

        meta["environment"] = ''.join(html.xpath("//*[@id='basic-info']/div[1]/span[5]/text()").extract()).replace("\r","").replace("\n","").replace("\t","").replace(" ","")

        meta["service"] = ''.join(html.xpath("//*[@id='basic-info']/div[1]/span[6]/text()").extract()).replace("\r","").replace("\n","").replace("\t","").replace(" ","")

        meta["tel"] = ''.join(html.xpath("//*[@id='basic-info']/p[1]/span[2]/text()").extract()).replace("\r","").replace("\n","").replace("\t","").replace(" ","")

        meta["review_num"] = ''.join(html.xpath("//*[@id='comment']/h2/a[2]/span/text()").extract()).replace(")", "").replace("(", "").replace("\r","").replace("\n","").replace("\t","").replace(" ","")

        # more_review = ''.join(html.xpath("//*[@id='comment']/p/a/@href").extract())
        more_review = ''.join(html.xpath(u"//a[contains(text(),'更多点评')]/@href").extract())

        review_url = meta["url"]+"/review_more#start=10"

        meta["review_urls"] = meta["url"]+"/review_more"

        yield Request(review_url, callback=self.parse_starts, meta=meta)

        del response

    def parse_starts(self, response):

        jobid = response.meta["jobid"]

        html = HtmlXPathSelector(response)

        meta = response.meta

        meta["start_5"] = ''.join(html.xpath(u"//a[text()='5星']/following-sibling::em/text()").extract()).replace(")", "").replace("(", "")

        meta["strat_4"] = ''.join(html.xpath(u"//a[text()='4星']/following-sibling::em/text()").extract()).replace(")", "").replace("(", "")

        meta["start_3"] = ''.join(html.xpath(u"//a[text()='3星']/following-sibling::em/text()").extract()).replace(")", "").replace("(", "")

        meta["start_2"] = ''.join(html.xpath(u"//a[text()='2星']/following-sibling::em/text()").extract()).replace(")", "").replace("(", "")

        meta["start_1"] = ''.join(html.xpath(u"//a[text()='1星']/following-sibling::em/text()").extract()).replace(")", "").replace("(", "")

        next_page = ''.join(html.xpath(u"//a[text()='下一页']/@href").extract())

        item = {}

        item["business_details"] = meta

        self.items.append(item)

        yield Request(urljoin(meta["review_urls"], "?pageno=1"), callback=self.parse_item, meta=meta)

        del response


    def parse_item(self, response):

        jobid = response.meta["jobid"]

        html = HtmlXPathSelector(response)

        meta = response.meta

        item = {}

        _item = []

        for comment in html.xpath("//*[@class='comment-list']/ul/li"):

            comments = {}

            comments["start"] = ''.join(comment.xpath(".//*[@class='user-info']/span/@title").extract()).replace("\r","").replace("\n","").replace("\t","").replace(" ","")

            comments["taste"] = ''.join(comment.xpath(u".//*[contains(text(),'口味')]/em/text()").extract()).replace(")", "").replace("(", "").replace("\r","").replace("\n","").replace("\t","").replace(" ","")

            comments["environment"] = ''.join(comment.xpath(u".//*[contains(text(),'环境')]/em/text()").extract()).replace(")", "").replace("(", "").replace("\r","").replace("\n","").replace("\t","").replace(" ","")

            comments["service"] = ''.join(comment.xpath(u".//*[contains(text(),'服务')]/em/text()").extract()).replace(")", "").replace("(", "").replace("\r","").replace("\n","").replace("\t","").replace(" ","")

            comments["review_text"] = ''.join(comment.xpath(".//*[@class='comment-txt']/div/text()").extract()).replace("\r","").replace("\n","").replace("\t","").replace(" ","")

            comments["review_time"] = ''.join(comment.xpath(".//*[@class='time']/text()").extract()).replace("\r","").replace("\n","").replace("\t","").replace(" ","")

            comments["discussant"] = ''.join(comment.xpath(".//*[@class='name']/a/text()").extract()).replace("\r","").replace("\n","").replace("\t","").replace(" ","")

            comments["discussant_contribution"] = ''.join(comment.xpath(".//*[@class='contribution']/span/@title").extract()).replace("\r","").replace("\n","").replace("\t","").replace(" ","")

            _item.append(comments)

        item["review_details"] = _item

        item["review_page"] = ''.join(html.xpath("//span[@class='PageSel']/text()").extract())

        self.items.append(item)

        next_page = ''.join(html.xpath(u"//a[text()='下一页']/@href").extract())

        if next_page:

            yield Request(urljoin(meta["review_urls"], next_page), callback=self.parse_item, meta=meta)

        del response

    def spider_closed(self, spider):

        item = {}

        items = {"items": self.items}

        if self.items[0]["status"] == 0:

            self.items[0]["status"] = 1  # 1代表程序正常爬取完成

            item["status"] = self.items[0]["status"]

            self.con.hmset(self.jobid, item)

            self.con.hmset(self.jobid, items)

            logging.warning(msg="dazhngdianping spider is OK!")

        else:

            item["status"] = self.items[0]["status"]

            self.con.hmset(self.jobid, item)

            self.con.hmset(self.jobid, items)

            logging.warning(msg="status error")

        logging.warning(msg="dazhngdianping spider closed")




