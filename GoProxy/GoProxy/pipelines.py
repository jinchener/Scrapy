# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import time
from scrapy.conf import settings

class GoproxyPipeline(object):
    def __init__(self):
        connection = pymongo.MongoClient(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        new_proxy = {
            "ip":item['ip'],
            "port":item['port'],
            "protocol":item['protocol'],
        }
        if self.collection.find_one(new_proxy) is None:
            self.collection.insert(new_proxy)

        return item
