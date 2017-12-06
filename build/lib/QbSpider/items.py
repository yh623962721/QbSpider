# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field


class JdItem(Item):

    #任务标识id
    jobid = Field()

    #爬取状态  0 正在爬取 1 ok 2 need phone vercode 3 图形验证码挂了 4 手机验证码错误
    status = Field()

    #爬虫爬行时间
    spidertime = Field()

    #用户名
    username = Field()

    #密码
    passwd = Field()

    #用户昵称

    usernickname = Field()

    #用户登录名
    userloginname = Field()

    #用户邮箱
    usermail = Field()

    #用户手机号
    userphone = Field()

    #用户身份证号
    useridcard = Field()

    #用户真实姓名
    userrealname = Field()

    #用户会员级别
    userrank = Field()

    #用户会员类型 企业用户或者个人用户
    usertype = Field()

    #余额
    balance = Field()

    #白条额度
    baitiaobalance = Field()

    #小金库
    wallet = Field()

    #昨天收益
    yesprofit = Field()

    # #银行卡名称
    # creditecard = Field()
    #
    # #银行卡类型
    # creditecardtype = Field()
    #
    # #银行卡卡号
    # creditecardno = Field()
    #
    # #持卡人姓名
    # owncardname = Field()
    #
    # #绑定的手机号
    # bandcardphone = Field()

    #订单id
    orderid = Field()

    #订单时间
    ordertime = Field()

    #付款时间
    paytime = Field()

    #订单金额
    ordercount = Field()

    #实际支付金额
    paycount = Field()

    #收货人
    receivername = Field()

    #收货人手机号
    receiverphone = Field()

    #收货地址
    receiveraddress = Field()

    #发票类型
    billtype = Field()

    #发票抬头
    billtitle = Field()

    #发票内容
    billcontent = Field()

    #当前订单中所有商品
    items = Field()

    #商品名称
    itemname = Field()

    #商品价格
    itemprice = Field()

    #商品数量
    itemnum = Field()

    #商品id
    itemid = Field()

    #商品url
    itemurl= Field()