# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

'''

class TestPipeline(object):
    def process_item(self, item, spider):
        return item
'''

# -*- coding: utf-8 -*-
#from twisted.enterprise import adbapi
import datetime
import MySQLdb.cursors


#from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
#from scrapy.crawler import Settings as settings
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class TestPipeline(object):

    def __init__(self):
        self.conn = MySQLdb.connect(host="127.0.0.1", port=3306,user="root",passwd="1900",db="scoredata",charset="utf8")
        self.cursor = self.conn.cursor()




    def process_item(self, item,spider):
        curTime = datetime.datetime.now()
        print type(item['zyid']),item['zyid']

        sql = """insert ignore into score20160719(schoolid,schoolname,specialtyname,localprovince,studenttype,year,batch,var,var_score,max,min,seesign,creat_at) values(%s, %s, %s, %s,%s, %s, %s, %s,%s,  %s，%s, %s, %s)"""
        param = (item['schoolid'],item['schoolname'],item['specialtyname'],item['localprovince'],item['studenttype'],item['year'],item['batch'],item['var'],item['var_score'],item['max'],item['min'],item['seesign'],curTime)
        #sql = """insert ignore into score20160719(schoolid,schoolname,specialtyname) values(%s, %s, %s)"""

        #param = (item['schoolid'],item['schoolname'],item['specialtyname'])

        try:
            self.cursor.execute(sql,param)
            self.conn.commit()
        except MySQLdb.Error, e:
            print 'Error %d %s' % (e.args[0], e.args[1])