#!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy
from test.items import TestItem
from urlparse import urljoin
from urlparse import urlparse
from urlparse import urlunparse
from posixpath import normpath
import json


class TestSpider(scrapy.Spider):
    name = "test"
    allowed_domains = ["gkcx.eol.cn"]
    start_urls = []
    for i in range(62749):#
        urld = 'http://data.api.gkcx.eol.cn/soudaxue/querySpecialtyScore.html?messtype=jsonp&url_sign=querySpecialtyScore&page=%s&size=50' % (
            i + 1 )
        start_urls.append(urld)

    def parse(self,response):
        text=response.text[5:][:-2]
        textjs = json.loads(text)
        for j in textjs['school']:
            item=TestItem()
            for (k,v) in j.items():
                item[k]=v.strip()
                print item[k]
            yield item
