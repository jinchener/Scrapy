# Spider for http proxy
# -*- coding: utf-8 -*-

import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from bs4 import BeautifulSoup
from GoProxy.items import GoproxyItem

import re

REG_IP = re.compile(r'((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))[^\d]*((\d){1,5})', re.M)

class ProxySpider(CrawlSpider):
    name = "Proxy"
    #allowed_domains = ['xici.net.co', 'youdaili.net']
    start_urls = [
            r"http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=ip%20proxy",
            r"http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=ip%20proxy&pn=10",
            r"http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=ip%20proxy&pn=20",
            r"http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=ip%20proxy&pn=30",
            r"http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=ip%20proxy&pn=40",
            r"http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=ip%20proxy&pn=50",
            r"http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=ip%20proxy&pn=60",
            r"http://www.gfsoso.net/?q=ip+proxy&t=1",
            r"http://www.gfsoso.net/?q=ip+proxy&pn=10",
            r"http://www.gfsoso.net/?q=ip+proxy&pn=20",
            r"http://www.gfsoso.net/?q=ip+proxy&pn=30",
            r"http://www.gfsoso.net/?q=ip+proxy&pn=40",
            r"http://www.gfsoso.net/?q=ip+proxy&pn=50",
            r"http://www.gfsoso.net/?q=ip+proxy&pn=60",
    ]

    rules = (
            Rule(LinkExtractor(allow=(r'',)), callback='parse_item'),
    )

    def parse_item(self, response):
        soup = BeautifulSoup(response.body)
        str_list = [ tag.string or '' for tag in soup.find_all(True) ]
        body_str = ' '.join(str_list)
        items = [ GoproxyItem(ip=group[0], port=group[7], protocol='HTTP') for group in re.findall(REG_IP, body_str) ]
        return items
