 #!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy
from lianjialist.items import LianjiaItem
from urlparse import urljoin
from urlparse import urlparse
from urlparse import urlunparse
from posixpath import normpath


class LianjiaSpider(scrapy.Spider):
    name = "lianjia"
    allowed_domains = ["lianjia.com"]
    start_urls = ["http://bj.lianjia.com/xiaoqu/"]

    def parse(self,response):
        pagenumtmp=response.xpath('/html/body/div[4]/div[1]/div[3]/div[2]/div/@page-data').extract()[0]
        pagenum=eval(pagenumtmp)["totalPage"]
        if pagenum>=100:
            if response.xpath('/html/body/div[3]/div[1]/dl[2]/dd/div/div[2]/a[1]/@href'):
                for href in response.xpath('/html/body/div[3]/div[1]/dl[2]/dd/div/div[2]/a[1]/@href'):
                    url=response.urljoin(href.extract())
                    yield scrapy.Request(url,callback=self.parse_list_page)
            else:
                for href in response.xpath('/html/body/div[3]/div[1]/dl[2]/dd/div/div/a/@href'):
                    url=response.urljoin(href.extract())
                    yield scrapy.Request(url,callback=self.parse)
        else:
            for i in range(pagenum):
                urltmp='pg%s/'%(i+1)
                url=response.urljoin(urltmp)
                yield scrapy.Request(url,callback=self.parse_list_page)


    def parse_loc2(self,response):
        pagenumtmp=response.xpath('/html/body/div[4]/div[1]/div[3]/div[2]/div/@page-data').extract()[0]
        pagenum=eval(pagenumtmp)["totalPage"]
        if pagenum>=100:
            for href in response.xpath('/html/body/div[3]/div[1]/dl[2]/dd/div/div[2]/a[1]/@href'):
                url=response.urljoin(href.extract())
                yield scrapy.Request(url,callback=self.parse_list_page)
        else:
            for i in range(pagenum):
                urltmp='pg%s/'%(i+1)
                url=response.urljoin(urltmp)
                yield scrapy.Request(url,callback=self.parse_list_page)


    def parse_list_page(self, response):
        #Items=[]
        for sel in response.xpath('/html/body/div[4]/div[1]/ul/li'):
            item = LianjiaItem()
            item['names']=sel.xpath('div[1]/div[1]/a/text()').extract()[0]
            item['types']=sel.xpath('div[1]/div[2]/a[1]/text()').extract()[0][1:-3]

            item['sales']=sel.xpath('div[1]/div[2]/a[2]/text()').extract()[0][5:-1]
            item['rents']=sel.xpath('div[1]/div[2]/a[3]/text()').extract()[0][:-5]
            item['locs1']=sel.xpath('div[1]/div[3]/a[1]/text()').extract()[0]
            item['locs2']=sel.xpath('div[1]/div[3]/a[2]/text()').extract()[0]
            item['years']=sel.xpath('div[1]/div[3]/text()[2]').extract()[0].replace(u"建成","").replace("/","").strip()
            item['prices']=sel.xpath('div[2]/div[1]/span/text()').extract()[0]
            item['counts']=sel.xpath('div[3]/a/span/text()').extract()[0]
            seltmp=sel.xpath('div[1]/div[4]/span')
            if len(seltmp)==2:
                item['schools']=sel.xpath('div[1]/div[4]/span[1]/text()').extract()[0]
                item['lines']=sel.xpath('div[1]/div[4]/span[2]/text()').extract()[0][3:]
            elif len(seltmp)==1:
                if u'号线'in seltmp.xpath('text()').extract()[0]:
                    item['lines']=seltmp.xpath('text()').extract()[0][3:]
                    item['schools']=u''
                else:
                    item['schools']=seltmp.xpath('text()').extract()[0]
                    item['lines']=u''
            else:
                item['schools']=u''
                item['lines']=u''
            item['url']=sel.xpath('div[1]/div[1]/a/@href').extract()[0]
            req=scrapy.Request(item['url'],meta={'item':item},callback=self.parse_page)
            yield req
            #yield req
        #print len(Items),len(Items[0])
        #yield Items


            #print item['schools'],'|',item['lines'],'|',item['years']


    def parse_page(self,response):
        item = response.meta['item']
        item['build']=response.xpath('//div[@class="xiaoquInfo"]/div[2]/span[2]/text()').extract()[0]
        item['prper']=response.xpath('//div[@class="xiaoquInfo"]/div[3]/span[2]/text()').extract()[0]
        item['comper']=response.xpath('//div[@class="xiaoquInfo"]/div[4]/span[2]/text()').extract()[0]
        item['devloper']=response.xpath('//div[@class="xiaoquInfo"]/div[5]/span[2]/text()').extract()[0]
        item['discribe']=response.xpath('//div[@class="xiaoquInfo"]/div[6]/span[2]/text()').extract()[0]
        item['building']=response.xpath('//div[@class="xiaoquInfo"]/div[7]/span[2]/text()').extract()[0]
        item['houses']=response.xpath('//div[@class="xiaoquInfo"]/div[8]/span[2]/text()').extract()[0]
        item['shop']=response.xpath('//div[@class="xiaoquInfo"]/div[9]/span[2]/span/text()').extract()[0]
        item['shopadd']=response.xpath('//div[@class="xiaoquInfo"]/div[9]/span[2]/text()').extract()[0]
        yield item





