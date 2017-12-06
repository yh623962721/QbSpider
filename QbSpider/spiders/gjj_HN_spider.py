# coding=utf-8
import json
import logging
import uuid
logger = logging.getLogger(__name__)
import time
from scrapy.exceptions import DontCloseSpider
from scrapy.http import Request,FormRequest
from scrapy.selector.lxmlsel import HtmlXPathSelector
from QbSpider.utils.utils import Util
from QbSpider.scrapy_redis.spiders import Spiders
from scrapy.spider import CrawlSpider
from scrapy import signals
from QbSpider.utils.RedisUtil import RedisConfUtil as rcu
import sys
from QbSpider.utils.hbclient import HbClient

reload(sys)
sys.setdefaultencoding("utf-8")

class gongjijinSpider(Spiders):

    name = "GJJ_HN"

    redis_key = "QUEUE_GJJ_HUNAN_KEY"

    custom_settings = {
        "COOKIES_ENABLED": True,
        "REDIRECT_ENABLED": True,#支不支持302跳转
        "LOGIN_TYPE": True,
        "DOWNLOAD_DELAY": 0,
        "DOWNLOAD_TIMEOUT": 120,
        "USELOCALIP": 1,
        "DOWNLOADER_MIDDLEWARES": {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': None,
            'QbSpider.middleware.RandomUserAgentMiddleware.RotateUserAgentMiddleware': 500,
            'QbSpider.middleware.RandomProxyMiddleware.ProxyMiddleware': 750,
        }
    }
    #handle_httpstatus_list = [302,301] #不用scrapy自己的302处理机制
    allowed_domains = []

    start_urlss = ["http://www.xzgjj.com:7001/wscx/index.jsp"]
    login_url = "http://www.xzgjj.com:7001/wscx/index.jsp"


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):

        spider = super(gongjijinSpider, cls).from_crawler(crawler, *args, **kwargs)

        crawler.signals.connect(spider.spider_closed, signals.spider_closed)

        return spider

    def __init__(self, *a, **kw):

        super(gongjijinSpider, self).__init__(*a, **kw)

        self.utils = Util()

        self.con = rcu().get_redis()

        self.con.ping()

        global null
        global false
        global true
        null = None
        false = False
        true = True

        self.sign = 0  # 标志位

        self.post_mx_url = "http://www.xzgjj.com:7001/wscx/zfbzgl/gjjmxcx/gjjmx_cx.jsp" #公积金明细查询

        self.post_dk_url = "http://www.xzgjj.com:7001/wscx/zfbzgl/dkxxcx/dkxx_cx.jsp" #公积金贷款信息查询

        self.post_xx_url = "http://www.xzgjj.com:7001/wscx/zfbzgl/gjjxxcx/gjjxx_cx.jsp" #公积金信息查询

        self.item_status = {"sign": ""}

        self.item_status_sign = 0
        self.idcard = ""
        self.token = ""

    # def start_requests(self):
    #
    #     meta = {}
    #
    #     yield Request(url=self.login_url, meta=meta)

    def parse(self, response):

        # self.meta = response.meta
        #
        self.idcard = response.meta["metass"].get("idcard","")
        # #
        self.password = response.meta["metass"].get("pwd","")#urllib.unquote(self.settings.get("PASSWORD", None))
        # #
        self.key = response.meta["metass"].get("key","")#
        # #
        self.token = response.meta["metass"].get("token","")#urllib.unquote(self.settings.get("JOBID", None))
        #
        self.vercode = response.meta["metass"].get("sms", "")

        self.item_status = {}

        logger.info(msg="<%s>,Get ready to login!!!"%self.idcard)

        url = "http://www.xzgjj.com:7001/wscx/zfbzgl/zfbzsq/login_hidden.jsp?"

        cxyd = "%B5%B1%C7%B0%C4%EA%B6%C8"

        get_data = "password=%s&sfzh=%s&cxyd=%s&dbname=gjjmx9&dlfs=0" % (self.password, self.idcard , cxyd)

        login_url = url + get_data

        yield Request(url=login_url,dont_filter=True,callback=self.parse_get_login)

    def parse_get_login(self, response):

        # f = open("parse_get_login.html","w")
        # f.write(response.body)
        # f.close()

        html = HtmlXPathSelector(response)

        self.cxyd = "当前年度"

        self.zgzh = ''.join(html.xpath("//*[@name='zgzh']/@value").extract()) ##职工账户

        self.sfzh = ''.join(html.xpath("//*[@name='sfzh']/@value").extract()) ##身份证号码

        self.zgxm = ''.join(html.xpath("//*[@name='zgxm']/@value").extract()) ##职工姓名

        self.dwbm = ''.join(html.xpath("//*[@name='dwbm']/@value").extract()) ##单位编码？

        self.zgzt = ''.join(html.xpath("//*[@name='zgzt']/@value").extract()) ##职工状态 ，当前状态

        if not self.zgxm and not self.zgzh or '错误' in response.body or '错误' in response.body.decode("gb2312", "ignore"):
            logger.error(msg="<%s>,Login HUNANGJJ error, password error!!!" % self.idcard)
            self.sign = 0
            self.item_status["code"] = 2104

            self.con.hmset(self.key, dict(self.item_status))

            # print u"密码输入错误2104"
            return
        else:
            self.item_status["code"] = 2102

            self.con.hmset(self.key, dict(self.item_status))
            logger.info(msg="<%s>,Login HUNANGJJ success!!!" % self.idcard)
            self.sign = 1
            # print u"登录成功2102"

        self.form_data = {
            "sfzh": str(self.sfzh),
            "zgxm": str(self.zgxm),
            "zgzh": str(self.zgzh),
            "dwbm": str(self.dwbm),
            "cxyd": str(self.cxyd),
            "zgzt": str(self.zgzt),
        }

        yield FormRequest(url=self.post_xx_url,formdata=self.form_data,callback=self.parse_get_xinxi,dont_filter=True)

        yield FormRequest(url=self.post_mx_url, formdata=self.form_data, callback=self.parse_get_mx,dont_filter=True)

        yield FormRequest(url=self.post_dk_url,formdata=self.form_data,callback=self.parse_get_daikuanxinxi,dont_filter=True)

    def parse_get_mx(self,response):
        logger.info(msg="<%s>,get HUNANGJJ MX!!!" % self.idcard)
        # f = open("parse_get_mx.html", "w")
        # f.write(response.body.decode("gb2312", "ignore"))
        # f.close()
        #print response.body.decode("gb2312", "ignore")

        html = HtmlXPathSelector(response)

        list_item = []

        for items in html.xpath("//*[@class='jtpsoft']"):

            item = {}

            item["payDate"] = ''.join(items.xpath(".//td[1]/text()").extract())   ##支付时间/日期

            if not item["payDate"]:
                continue

            item["balanceRmb"] = ''.join(items.xpath(".//td[4]/text()").extract())  ##余额

            item["payType"] = ''.join(items.xpath(".//td[6]/text()").extract())  #缴费类型/摘要

            item["debtorRmb"] = ''.join(items.xpath(".//td[2]/text()").extract())  ##借方金额

            item["lenderRmb"] = ''.join(items.xpath(".//td[3]/text()").extract())  ##贷方金额

            item["trend"] = ''.join(items.xpath(".//td[5]/text()").extract())    #借贷方向

            list_item.append(item)

        if not list_item:
            self.sign = 0
            self.item_status["fatch_code"] = 2199

            self.con.hmset(self.key, dict(self.item_status))

            logger.error(msg="<%s>,get HUNANGJJ MX NO DATA!!!" % self.idcard)

            # print u"采集失败，没采到数据！2199"

        else:

            dic_item = {"detail_info": list_item}

            self.tb = HbClient()

            self.tb.insert(colname=u"公积金-湖南-明细查询 ",url=response.url,html=response.body,struct_dic=dic_item,
                           id=self.idcard, post_dic=self.form_data, token=self.token)

            logger.info(msg="<%s>,get HUNANGJJ MX OVER!!!" % self.idcard)

    def parse_get_xinxi(self,response):
        logger.info(msg="<%s>,get HUNANGJJ XX!!!" % self.idcard)
        # f = open("parse_get_xinxi.html","w")
        # f.write(response.body.decode("gb2312", "ignore"))
        # f.close()

        html = HtmlXPathSelector(response)

        item = {}

        item["realName"] = ''.join(html.xpath(u"//td[text()='职工姓名']/../td[2]//text()").extract()).strip()

        #item["银行账号"] = ''.join(html.xpath("//tr[@class='jtpsoft'][1]/td[4]/font/text()").extract()).strip()

        item["idCard"] = ''.join(html.xpath(u"//td[text()='身份证号']/../td[2]//text()").extract()).strip()

        if item["idCard"]:
            item["birthday"] = item["idCard"][6:14]
            sex = item["idCard"][-2]
            if int(sex) % 2 == 1:      ####偶数为女，奇数为男
                item["sex"] = u"男"
            elif int(sex) % 2 == 0:
                item["sex"] = u"女"
            else:
                item["sex"] = ""
        else:
            item["sex"] = ""
            item["birthday"] = ""

        #item["职工账号"] = ''.join(html.xpath("//tr[@class='jtpsoft'][2]/td[4]/font/text()").extract()).strip()

        item["comName"] = ''.join(html.xpath(u"//td[text()='所在单位']/../td[2]//text()").extract()).strip()

        item["officeName"] = ''.join(html.xpath(u"//td[text()='所属办事处']/../td[4]//text()").extract()).strip()

        item["startDate"] = ''.join(html.xpath(u"//td[text()='开户日期']/../td[2]//text()").extract()).strip()

        item["fundStatus"] = ''.join(html.xpath(u"//td[text()='当前状态']/../td[4]//text()").extract()).strip()

        item["monthPayBase"] = ''.join(html.xpath(u"//td[text()='月缴基数']/../td[2]//text()").extract()).strip()

        item["fundRatio"] = ''.join(html.xpath(u"//td[text()='缴存比例']/../td[5]//text()").extract()).strip()

        item["monthPayRmb"] = ''.join(html.xpath(u"//td[text()='月缴金额']/../td[2]//text()").extract()).strip()

        item["lastYearBalanceRmb"] = ''.join(html.xpath(u"//*[text()='上年余额']/../../td[4]//text()").extract()).strip()

        item["comRmb"] = ''.join(html.xpath(u"//td[text()='单位月缴额']/../td[2]//text()").extract()).strip()

        item["yearRepayRmb"] = ''.join(html.xpath(u"//*[text()='本年补缴']/../../td[4]//text()").extract()).strip()

        item["perRmb"] = ''.join(html.xpath(u"//td[text()='个人月缴额']/../td[2]//text()").extract()).strip()

        item["yearDrawRmb"] = ''.join(html.xpath(u"//*[text()='本年支取']/../../td[4]//text()").extract()).strip()

        item["yearPayRmb"] = ''.join(html.xpath(u"//td[text()='本年缴交']/../td[2]//text()").extract()).strip()

        item["yearAccrual"] = ''.join(html.xpath(u"//*[text()='本年利息']/../../td[4]//text()").extract()).strip()

        item["yearSwitchInRmb"] = ''.join(html.xpath(u"//td[text()='本年转入']/../td[2]//text()").extract()).strip()

        item["balance"] = ''.join(html.xpath(u"//*[text()='公积金余额']/../../td[4]//text()").extract()).strip()

        item["endDate"] = ''.join(html.xpath(u"//td[text()='缴至年月']/../td[2]//text()").extract()).strip()

        logger.info(msg="<%s>,get HUNANGJJ XX OVER!!!" % self.idcard)

        if not item:

            self.sign = 0
            self.item_status["fatch_code"] = 2199

            self.con.hmset(self.key, dict(self.item_status))

            # print u"采集失败，没采到数据！2199"

            logger.info(msg="<%s>,get HUNANGJJ XX NO DATA!!!" % self.idcard)

        else:
            self.tb = HbClient()

            self.tb.insert(colname=u"公积金-湖南-信息查询 ", url=response.url, html=response.body, struct_dic={"basic_info":[item]},
                           id=self.idcard, post_dic=self.form_data, token=self.token)

            logger.info(msg="<%s>,get HUNANGJJ XX OVER!!!" % self.idcard)


    def parse_get_daikuanxinxi(self,response):
        logger.info(msg="<%s>,get HUNANGJJ DKXX!!!" % self.idcard)
        # f = open("parse_get_daikuanxinxi.html", "w")
        # f.write(response.body.decode("gb2312", "ignore"))
        # f.close()

        if "该职工没有贷款".encode("gb2312", "ignore") in response.body:
            logger.info(msg="<%s>,DKXX NO DATA!!!" % self.idcard)
            # print u"该职工没有贷款"
            return

        html = HtmlXPathSelector(response)

        item = {}

        #item["贷款合同编号"] = ''.join(html.xpath("//tr[@class='jtpsoft'][1]/td[2]//text()").extract()).strip()

        item["userName"] = ''.join(html.xpath(u"//td[text()='姓名']/../td[4]//text()").extract()).strip()

        item["loanMoney"] = ''.join(html.xpath(u"//td[text()='贷款金额']/../td[2]//text()").extract()).strip()

        loanLimit = ''.join(html.xpath(u"//td[text()='贷款年限']/../td[4]//text()").extract()).strip() ##贷款年限
        if loanLimit:
            loanLimit_year = loanLimit.replace("年", "").replace(u"年", "")
            item["loanLimit"] = int(loanLimit_year)*12
        else:
            item["loanLimit"] = ""
        item["repaidPrincipal"] = ''.join(html.xpath(u"//td[text()='已还本金']/../td[2]//text()").extract()).strip()

        item["repaidInterest"] = ''.join(html.xpath(u"//td[text()='已还利息']/../td[4]//text()").extract()).strip()

        item["loanBalance"] = ''.join(html.xpath(u"//td[text()='贷款余额']/../td[2]//text()").extract()).strip()

        item["monthLeastRepayment"] = ''.join(html.xpath(u"//td[text()='月最低还款']/../td[4]//text()").extract()).strip()

        item["overdueMoney"] = ''.join(html.xpath(u"//td[text()='当前逾期金额']/../td[2]//text()").extract()).strip()

        item["overdueAccrual"] = ''.join(html.xpath(u"//td[text()='当前逾期利息']/../td[4]//text()").extract()).strip()

        item["repaidDay"] = ''.join(html.xpath(u"//td[text()='月还款日']/../td[2]//text()").extract()).strip()

        #item["还至年月"] = ''.join(html.xpath("//tr[@class='jtpsoft'][6]/td[4]//text()").extract()).strip()

        item["loanDay"] = ''.join(html.xpath(u"//td[text()='放款日期']/../td[2]//text()").extract()).strip()

        item["entrustBank"] = ''.join(html.xpath(u"//td[text()='受托银行']/../td[4]//text()").extract()).strip()

        item["loanInterestRate"] = ''.join(html.xpath(u"//td[text()='贷款利率']/../td[2]//text()").extract()).strip()

        item["overdueTimes"] = ''.join(html.xpath(u"//td[text()='当前逾期期数']/../td[4]//text()").extract()).strip()

        item["repaidType"] = ''.join(html.xpath(u"//td[text()='还款方式']/../td[2]//text()").extract()).strip()

        item["securityType"] = ''.join(html.xpath(u"//td[text()='担保方式']/../td[4]//text()").extract()).strip()

        item["loanType"] = ''.join(html.xpath(u"//td[text()='购房类型']/../td[2]//text()").extract()).strip()

        #item["历史逾期金额"] = ''.join(html.xpath("//tr[@class='jtpsoft'][10]/td[4]//text()").extract()).strip()

        #item["历史逾期期数"] = ''.join(html.xpath("//tr[@class='jtpsoft'][11]/td[2]//text()").extract()).strip()

        item["monthHedging"] = ''.join(html.xpath(u"//td[text()='是否办理月对冲']/../td[4]//text()").extract()).strip()

        logger.info(msg="<%s>,get HUNANGJJ DKXX OVER!!!" % self.idcard)

        self.tb = HbClient()

        self.tb.insert(colname=u"公积金-湖南-贷款信息查询 ", url=response.url, html=response.body, struct_dic={"loan_info":[item]},
                       id=self.idcard, post_dic=self.form_data, token=self.token)

    def spider_idle(self):

        if self.idcard:
            row_key = "GJJ_HUNAN_%s_%s" % (self.idcard, self.token)
            # print row_key, '90000000000000000000000000000000000'
            self.con.publish("gjj_k", row_key)

        if self.sign == 1:
            self.item_status["fatch_code"] = 2101

            self.con.hmset(self.key, dict(self.item_status))
            logger.info(msg="<%s>,crawl Success!!!2101" % self.idcard)
            # print u"采集成功 2101"
            # print "crawl success 2101 "
        if self.item_status == {}:

            self.item_status["fatch_code"] = 2199

            self.con.hmset(self.key, dict( self.item_status ))

            logger.error(msg="<%s>【程序代码错误，没有采集到数据】【ErrorCode=2199】" % self.idcard)
        # else:   #代码错误重新登录，由前端控制！
        #     if self.item_status == {}:
        #
        #         self.item_status_sign += 1
        #
        #         if self.item_status_sign < 3:
        #
        #             logger.error(msg="<%s>,error---------------!!!" % self.idcard)
        #
        #             # print u"程序代码错误,重新开始登录！！"
        #             logger.error(msg="<%s>,程序代码错误,重新开始登录！！" % self.idcard)
        #
        #             item = {}
        #
        #             item["idcard"] = self.idcard
        #
        #             item["pwd"] = self.password
        #
        #             item["key"] = self.key
        #
        #             item["token"] = self.token
        #
        #             item["sms"] = self.vercode
        #
        #             yield Request(url=self.start_urlss[0], meta={"metass": json.loads(item)}, dont_filter=True)
        #
        #             raise DontCloseSpider

        #print "schedule_next_requests___DontCloseSpider__spider_idle"
        self.item_status_sign = 0
        self.idcard = ""
        self.token = ""
        self.item_status = {"sign": ""}

        self.sign = 0

        self.schedule_next_requests()

        raise DontCloseSpider

    def spider_closed(self, spider):

        if self.sign == 1:
            self.item_status["fatch_code"] = 2101

            self.con.hmset(self.key, dict(self.item_status))

            logger.info(msg="<%s>,crawl Success!!!2101" % self.idcard)

            # print u"采集成功 2101"
            # print "crawl success 2101"

        self.sign = 0

        logging.warning(msg="gongjijin spider closed")
