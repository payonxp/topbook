# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field


class TopbookItem(Item):
    # define the fields for your item here like:
    book_name = Field()
    author = Field()
    time = Field()
    content = Field()
    vote = Field()
    pass
