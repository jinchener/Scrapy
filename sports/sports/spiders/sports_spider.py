#!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy
from sports.items import SportsItem
from urlparse import urljoin
from urlparse import urlparse
from urlparse import urlunparse
from posixpath import normpath
import re


class SportsSpider(scrapy.Spider):
    name = "sports"
    start_urls = []
    sportsdic={'1':'游泳','2':'跳水','3':'花样游泳','4':'水球','5':'射箭','6':'田径','7':'羽毛球','8':'篮球','9':'棒球','10':'健美','11':'保龄球','12':'拳击','13':'皮划艇','14':'国际象棋','15':'台球','16':'自行车','17':'马术','18':'击剑','19':'足球','20':'高尔夫','21':'体操','22':'艺术体操','23':'蹦床','24':'手球','25':'曲棍球','26':'柔道','27':'赛艇','28':'橄榄球','29':'帆船','30':'藤球','31':'射击','32':'垒球','33':'软式网球','34':'壁球','35':'乒乓球','36':'跆拳道','37':'网球','38':'铁人三项','39':'排球','40':'沙滩排球','41':'举重','42':'摔跤','43':'武术','44':'短道速度滑冰','45':'速度滑冰','46':'花样滑冰','47':'冰球','48':'冰壶','49':'越野滑雪','50':'高山滑雪','51':'冬季两项','52':'自由式滑雪','53':'单板滑雪'}
    for sport in sportsdic:
        url='http://data.star.sports.cn/list.php?key=&pid=%s'%(sport)

        start_urls.append(url)

    def parse(self,response):
        urlpro=response.url
        if response.xpath("//font[2]/text()").extract():
            pagenums=response.xpath("//font[2]/text()").extract()[0]
            for i in range(int(pagenums)):
                suburl=urlpro+u'&page=%s'%(i+1)
                yield scrapy.Request(suburl,callback=self.parse_detail)
        else:
            yield scrapy.Request(urlpro,callback=self.parse_detail)

    def parse_detail(self,response):
        url=response.url
        pagep=re.compile(r'page=[0-9]{0,2}')
        pidp=re.compile(r'pid=[0-9]{0,2}')
        if pagep.findall(url):
            page=pagep.findall(url)[0][5:]
        else:
            page='1'
        pid=pidp.findall(url)[0][4:]
        namelist=response.xpath("//div[@class=\"piclist\"]/a/text()[3]").extract()
        print page,len(namelist)
        for i in namelist:
            item=SportsItem()
            item['pid']=pid
            item['pagenum']=page
            item['sport']=self.sportsdic[pid]
            item['name']=i.strip()
            item['url']=url
            yield item
