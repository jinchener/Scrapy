# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TestItem(scrapy.Item):

    # define the fields for your item here like:
    # name = scrapy.Field()
    schoolid=scrapy.Field()
    schoolname=scrapy.Field()
    specialtyname=scrapy.Field()
    localprovince=scrapy.Field()
    studenttype=scrapy.Field()
    year=scrapy.Field()
    batch=scrapy.Field()
    var=scrapy.Field()
    var_score=scrapy.Field()
    max=scrapy.Field()
    min=scrapy.Field()
    zyid=scrapy.Field()
    url=scrapy.Field()
    seesign=scrapy.Field()
    urlcount=scrapy.Field()
    pass
