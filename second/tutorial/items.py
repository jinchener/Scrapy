# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LianjiaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    names=scrapy.Field()
    types=scrapy.Field()
    sales=scrapy.Field()
    rents=scrapy.Field()
    locs1=scrapy.Field()
    locs2=scrapy.Field()
    years=scrapy.Field()
    prices=scrapy.Field()
    counts=scrapy.Field()
    schools=scrapy.Field()
    lines=scrapy.Field()
    url=scrapy.Field()
    build=scrapy.Field()
    prper=scrapy.Field()
    comper=scrapy.Field()
    devloper=scrapy.Field()
    discribe=scrapy.Field()
    building=scrapy.Field()
    houses=scrapy.Field()
    shop=scrapy.Field()
    shopadd=scrapy.Field()


    pass
