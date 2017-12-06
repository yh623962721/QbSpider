# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field


class LieBiaoItem(Item):

    #任务标识id
    jobid = Field()

    #爬取状态  0 正在爬取 1 ok 3程序出错
    status = Field()

    #爬虫爬行时间
    spidertime = Field()

    #抓取时间
    creat_time = Field()

    # 城市
    city = Field()





