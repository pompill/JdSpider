# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.conf import settings


class JdPipeline(object):
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
        self.Jd = self.client[settings['MONGO_DB']]
        self.JdData = self.Jd[settings['MONGO_COLL']]
        pass

    def process_item(self, item, spider):
        self.JdData.insert_one(item)
        return item

    def close_spider(self, spider):
        pass
