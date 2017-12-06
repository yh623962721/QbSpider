# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field


class DZDPItem(Item):

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

    # 城市编号(大众点评排的)
    cityid = Field()

    # 商户名称
    vendor_name = Field()

    # 区域名称
    district_name = Field()

    # 抓取商户数量
    Effective_num = Field()

    # 商户类别
    type = Field()

    # 商户所在商圈名称
    business_district = Field()

    # 商户所在链接地址
    url = Field()

    # 所在行政区同类别美食商户总数
    district_type_num = Field()

    # 所在行政区美食商户总数
    district_num = Field()

    # 商户所在人气指数（同区域对比排名）
    popularity_ranking = Field()

    #该区域或者该商圈对应大众点评中的KEY值
    district_key = Field()

    #商户号
    shopid = Field()

    # 商户总体星级
    start = Field()

    # 人均消费(人民币元)
    mean_price = Field()

    # 地址
    address = Field()

    # 总体口味
    taste = Field()

    # 总体环境
    environment = Field()

    # 总体服务
    service = Field()

    # 电话
    tel = Field()

    # 全部评论数量
    review_num = Field()

    # 5星评论数量
    start_5 = Field()

    # 4星评论数量
    start_4 = Field()

    # 3星评论数量
    start_3 = Field()

    # 2星评论数量
    start_2 = Field()

    # 1星评论数量
    start_1 = Field()

    # 商户详细信息
    business_details = Field()

    # 评论详情
    review_details = Field()

    # 评论星级
    review_start = Field()

    # 口味评价
    review_taste = Field()

    # 环境评价
    review_environment = Field()

    # 服务评价
    review_service = Field()

    # 客户评论
    review_text = Field()

    # 客户评价时间
    review_time = Field()

    # 评价人名称
    discussant = Field()

    # 评价人贡献值（级别）
    discussant_contribution = Field()

    # 评论页数
    review_page = Field()



