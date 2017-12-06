# coding=utf-8
import requests
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
import sys,os
sys.path.append(os.path.abspath("../../"))
from QbSpider.utils.RedisUtil import RedisConfUtil as rcu

if __name__ == "__main__":
    spider_name = "jingdong"
    username = "654705983@qq.com"
    passwd = "qq654705983"
    vercode = ""
    #useproxyhighlevel = False

    #pay_load = ["spider=%s"%spider_name,"username=%s"%username,"passwd=%s"%passwd,"vercode=%s"%vercode,"spidertype=realtime"]

    #url = "http://172.28.40.23:9999/schedule?%s"%("&".join(pay_load))

    pay_load = {"spider" :spider_name, "username" : username, "passwd" : passwd, "vercode" : vercode,
                "spidertype":"realtime","logintype":2}

    url = "http://172.28.40.23:9999/schedule"

    r = requests.get(url,params=pay_load)

    jobid = r.text

    print jobid





    # import urllib
    # import sys
    # codecs = sys.stdin.encoding
    # spider_name = "dianpingsss"
    # username = None
    # city = "北京"
    # vendor = "金掌勺"
    # passwd = None
    # vercode = None
    #
    # pay_load = {"spider": spider_name, "city": city, "vendor": vendor, "vercode": vercode}
    #
    # r = requests.post("http://localhost:8001/schedule",data=pay_load)
    #
    # print r.text

