# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field


class CNINFO_Item(Item):

    body = Field()

    url = Field()

    path = Field()



