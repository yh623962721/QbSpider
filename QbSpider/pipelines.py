# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import sys
# reload(sys)
# sys.setdefaultencoding("utf8")


class QbspiderPipeline(object):
    def process_item(self, item, spider):
        return item

class XinlangPipeline(object):

    def __init__(self, settings):
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_item(self, item, spider):

        mysqlset = self.settings.getdict("PROXY_MYSQL_QIHUO")
        conn = MySQLdb.connect(
            host=mysqlset['Host'],
            port=mysqlset['Port'],
            user=mysqlset['User'],
            passwd=mysqlset['Passwd'],
            charset=mysqlset['Charset']
        )
        # cur = conn.cursor(pymysql.cursors.DictCursor)
        cur = conn.cursor()
        conn.select_db(mysqlset['Db'])
        dictionary = [
             'txt_time', 'columnName', 'columnLink', 'informationSources', 'title', 'titleLink', 'keyword'
            , 'desc', 'txt', 'img'
        ]
        items = [item[x] for x in dictionary]

        sql = """
            INSERT into xinlang_qihuo (`txt_time`,`columnName`,`columnLink`,`informationSources`,`title`,
            `titleLink`,`keyword`,`desc`,`txt`,`img`,`creat_time`) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',NOW())
            """ % tuple(items)

        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()

class HexunPipeline(object):

    def __init__(self, settings):
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_item(self, item, spider):

        mysqlset = self.settings.getdict("PROXY_MYSQL_QIHUO")
        conn = MySQLdb.connect(
            host=mysqlset['Host'],
            port=mysqlset['Port'],
            user=mysqlset['User'],
            passwd=mysqlset['Passwd'],
            charset=mysqlset['Charset']
        )
        # cur = conn.cursor(pymysql.cursors.DictCursor)
        cur = conn.cursor()
        conn.select_db(mysqlset['Db'])
        dictionary = [
            'txt_id', 'txt_time', 'columnName', 'columnLink', 'informationSources', 'title', 'titleLink', 'desc'
            , 'txt', 'img'
        ]
        items = [item[x] for x in dictionary]

        sql = """
            INSERT into hexun_qihuo (`txt_id`,`txt_time`,`columnName`,`columnLink`,`informationSources`,`title`,
            `titleLink`,`desc`,`txt`,`img`,`creat_time`) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',NOW())
            """ % tuple(items)

        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()

class WaiHuiHangQingPipeline(object):

    def __init__(self, settings):
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_item(self, item, spider):

        mysqlset = self.settings.getdict("PROXY_MYSQL_HUILV")
        conn = MySQLdb.connect(
            host=mysqlset['Host'],
            port=mysqlset['Port'],
            user=mysqlset['User'],
            passwd=mysqlset['Passwd'],
            charset=mysqlset['Charset']
        )
        # cur = conn.cursor(pymysql.cursors.DictCursor)
        cur = conn.cursor()
        conn.select_db(mysqlset['Db'])
        dictionary = [
            'code', 'time', 'buying_rate', 'selling_rate', 'zuo_shou_jia', 'amplitude', 'at_the_opening', 'maximum_price'
            , 'minimum_price', 'recent_quotation', 'name', 'date'
        ]
        items = [item[x] for x in dictionary]
        if item["type"] == "zhipan":
            sql = """
                        INSERT into waihui_zhipan (`code`,`time`,`buying_rate`,`selling_rate`,`zuo_shou_jia`,`amplitude`,
                        `at_the_opening`,`maximum_price`,`minimum_price`,`recent_quotation`,`name`,`date`,`creat_time`) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',NOW())
                        """ % tuple(items)
            cur.execute(sql)
            conn.commit()
            sql = """UPDATE waihui_zhipan_update SET time = '%s', buying_rate = '%s',selling_rate = '%s',zuo_shou_jia = '%s',
            amplitude = '%s',at_the_opening = '%s',maximum_price = '%s',minimum_price = '%s',recent_quotation = '%s',
            name = '%s',date = '%s', update_time=NOW() WHERE code = '%s'"""%(item["time"], item["buying_rate"], item["selling_rate"], item["zuo_shou_jia"],
                                                          item["amplitude"], item["at_the_opening"], item["maximum_price"], item["minimum_price"],
                                                          item["recent_quotation"], item["name"], item["date"], item["code"], )

            cur.execute(sql)
            conn.commit()
        elif item["type"] == "jiaochapan":
            sql = """
                        INSERT into waihui_jiaochapan (`code`,`time`,`buying_rate`,`selling_rate`,`zuo_shou_jia`,`amplitude`,
                        `at_the_opening`,`maximum_price`,`minimum_price`,`recent_quotation`,`name`,`date`,`creat_time`) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',NOW())
                        """ % tuple(items)
            cur.execute(sql)
            conn.commit()
            sql = """UPDATE waihui_jiaochapan_update SET time = '%s', buying_rate = '%s',selling_rate = '%s',zuo_shou_jia = '%s',
                        amplitude = '%s',at_the_opening = '%s',maximum_price = '%s',minimum_price = '%s',recent_quotation = '%s',
                        name = '%s',date = '%s', update_time=NOW() WHERE code = '%s'""" % (
            item["time"], item["buying_rate"], item["selling_rate"], item["zuo_shou_jia"],
            item["amplitude"], item["at_the_opening"], item["maximum_price"], item["minimum_price"],
            item["recent_quotation"], item["name"], item["date"], item["code"],)

            cur.execute(sql)
            conn.commit()
        cur.close()
        conn.close()

class HexunWaihuiPipeline(object):
    def __init__(self, settings):
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_item(self, item, spider):

        mysqlset = self.settings.getdict("PROXY_MYSQL_WAIHUI")
        conn = MySQLdb.connect(
            host=mysqlset['Host'],
            port=mysqlset['Port'],
            user=mysqlset['User'],
            passwd=mysqlset['Passwd'],
            charset=mysqlset['Charset']
        )
        # cur = conn.cursor(pymysql.cursors.DictCursor)
        cur = conn.cursor()
        conn.select_db(mysqlset['Db'])
        dictionary = [
             'txt_time', 'columnName', 'columnLink', 'informationSources', 'title', 'titleLink', 'desc'
            , 'txt', 'img'
        ]
        items = [item[x] for x in dictionary]

        sql = """
            INSERT into hexun_waihui (`txt_time`,`columnName`,`columnLink`,`informationSources`,`title`,
            `titleLink`,`desc`,`txt`,`img`,`creat_time`) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s',NOW())
            """ % tuple(items)

        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()

class DailyFXPipeline(object):
    def __init__(self, settings):
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_item(self, item, spider):

        mysqlset = self.settings.getdict("PROXY_MYSQL_WAIHUI")
        conn = MySQLdb.connect(
            host=mysqlset['Host'],
            port=mysqlset['Port'],
            user=mysqlset['User'],
            passwd=mysqlset['Passwd'],
            charset=mysqlset['Charset']
        )
        # cur = conn.cursor(pymysql.cursors.DictCursor)
        cur = conn.cursor()
        conn.select_db(mysqlset['Db'])
        dictionary = [
             'txt_time', 'columnName', 'columnLink', 'informationSources', 'title', 'titleLink', 'desc'
            , 'txt', 'img'
        ]
        items = [item[x] for x in dictionary]

        sql = """
            INSERT into DailyFX_waihui (`txt_time`,`columnName`,`columnLink`,`informationSources`,`title`,
            `titleLink`,`desc`,`txt`,`img`,`creat_time`) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s',NOW())
            """ % tuple(items)

        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()

class ForexPipeline(object):
    def __init__(self, settings):
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_item(self, item, spider):

        mysqlset = self.settings.getdict("PROXY_MYSQL_WAIHUI")
        conn = MySQLdb.connect(
            host=mysqlset['Host'],
            port=mysqlset['Port'],
            user=mysqlset['User'],
            passwd=mysqlset['Passwd'],
            charset=mysqlset['Charset']
        )
        # cur = conn.cursor(pymysql.cursors.DictCursor)
        cur = conn.cursor()
        conn.select_db(mysqlset['Db'])
        dictionary = [
             'txt_time', 'columnName', 'columnLink', 'informationSources', 'title', 'titleLink', 'desc', 'tags'
            , 'txt', 'img', 'scenarist'
        ]
        items = [item[x] for x in dictionary]

        sql = """
            INSERT into forex_waihui (`txt_time`,`columnName`,`columnLink`,`informationSources`,`title`,
            `titleLink`,`desc`,`tags`,`txt`,`img`,`scenarist`,`creat_time`) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',NOW())
            """ % tuple(items)

        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()

class KitcoPipeline(object):
    def __init__(self, settings):
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_item(self, item, spider):

        mysqlset = self.settings.getdict("PROXY_MYSQL_WAIHUI")
        conn = MySQLdb.connect(
            host=mysqlset['Host'],
            port=mysqlset['Port'],
            user=mysqlset['User'],
            passwd=mysqlset['Passwd'],
            charset=mysqlset['Charset']
        )
        # cur = conn.cursor(pymysql.cursors.DictCursor)
        cur = conn.cursor()
        conn.select_db(mysqlset['Db'])
        dictionary = [
             'txt_time', 'columnName', 'columnLink', 'informationSources', 'title', 'titleLink', 'desc'
            , 'txt', 'img'
        ]
        items = [item[x] for x in dictionary]

        sql = """
            INSERT into kitco_waihui (`txt_time`,`columnName`,`columnLink`,`informationSources`,`title`,
            `titleLink`,`desc`,`txt`,`img`,`creat_time`) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s',NOW())
            """ % tuple(items)

        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()