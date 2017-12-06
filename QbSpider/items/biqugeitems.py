# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field


class BiQuGe_Item(Item):
    page_name = Field()

    page_url = Field()

    txt = Field()

    name = Field()

    book_type = Field()

    url = Field()

    path = Field()



