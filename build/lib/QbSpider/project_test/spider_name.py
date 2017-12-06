# coding=utf-8
from scrapy.spider import CrawlSpider
from scrapy.selector.lxmlsel import HtmlXPathSelector
from twisted.internet import reactor
from scrapy.crawler import CrawlerProcess

class dianpingSpider(CrawlSpider):
    name = "crawl"

    allowed_domains = []

    start_urls = ["http://www.dianping.com/beijing/food"]

    def parse(self, response):


        hxs = HtmlXPathSelector(response)

        print "*"*66

        print hxs.xpath("//script[@class='J_auto-load']/text()").extract()

        print "-"*66

        return


class StartSpider(object):

    def crawl(self):

        from scrapy.utils.project import get_project_settings

        settings = get_project_settings()

        runner = CrawlerProcess(settings)

        d = runner.crawl(dianpingSpider)

        #d = runner.crawl(JdItemSpider)

        d.addBoth(lambda _: reactor.stop())

        reactor.run()





if __name__ == "__main__":

    print StartSpider().crawl()

