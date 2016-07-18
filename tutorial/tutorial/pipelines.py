# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from openpyxl import Workbook

class LianjiaPipeline(object):  # 设置工序一
    def __init__(self):
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(['小区名', '30天成交数', '正在出租', '区1', '区2', '年份', '均价', '出售数', '学校', '地铁'])  # 设置表头


    def process_item(self, item, spider):  # 工序具体内容
        line = [item['names'], item['sales'], item['rents'], item['locs1'], item['locs2'], item['years'], item['prices'], item['counts'], item['schools'], item['lines']]  # 把数据中每一项整理出来
        self.ws.append(line)  # 将数据以行的形式添加到xlsx中
        self.wb.save('tuniu.xlsx')  # 保存xlsx文件
        return item

