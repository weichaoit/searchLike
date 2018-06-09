# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
import codecs
import json
import pymysql
import pymysql.cursors
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if 'image_path' in item:
            for k,v in results:
                image_file_path = v['path']

            item['image_path'] = image_file_path
        return item


class JsonExporterPipeline(object):
    '''
    调用scrapy提供的jsonexporter
    '''
    def __init__(self):
        self.file = open('article2.json','wb')
        self.exporter = JsonItemExporter(self.file,encoding='utf-8',ensure_ascii=False)

    def close_spider(self,spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self,item,spider):
        self.exporter.export_item(item)
        return item


class JsonPipeline(object):
    '''
    自定义的json
    '''
    def __init__(self):
        self.file = codecs.open('article.json','w',encoding='utf-8')

    def process_item(self,item,spider):
        lines = json.dumps(dict(item),ensure_ascii=False)+'\n'
        self.file.write(lines)
        return item

    def spider_close(self,spider):
        self.file.close()


class MysqlPipeline(object):
    '''
    保存到MySQL中
    采用同步的机制写入
    '''
    def __init__(self):
        self.conn = pymysql.connect('192.168.1.103','root','123456','mydata',charset='utf8',use_unicode=True)
        self.cursor = self.conn.cursor()


    def process_item(self,item,spider):
        insert_sql = "insert into jobbole_article(title,create_time,url,url_object_id,image_url,image_path,comment_nums,shoucang_nums,praise_nums,tag_lists,content) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(item['title'],item['create_time'],item['url'],item['url_object_id'],item['image_url'],item['image_path'],item['comment_nums'],item['shoucang_nums'],item['praise_nums'],item['tag_lists'],item['content'])
        self.cursor.execute(insert_sql)

        self.conn.commit()


class MysqlTwistedPipeline(object):
    '''
    采用异步写入MySQL
    '''
    def __init__(self,dbpool):
        self.pool = dbpool

    @classmethod
    def from_settings(cls,settings):

        dbparms = dict(
            host=settings['MYSQL_HOST'],
            user = settings['MYSQL_USER'],
            passwd = settings['MYSQL_PASSWORD'],
            db = settings['MYSQL_DBNAME'],
            charset = 'utf8',
            cursorclass = pymysql.cursors.DictCursor,
            use_unicode = True,
        )

        # 连接池
        dbpool = adbapi.ConnectionPool('pymysql',**dbparms)

        return cls(dbpool)


    def process_item(self,item,spider):
        # 执行异步插入
        query = self.pool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error)


    def do_insert(self,cursor,item):
        # 插入
        # insert_sql = "insert into jobbole_article(title,url,url_object_id,create_time,shoucang_nums) VALUES ('%s','%s','%s','%s','%s')" % (
        # item['title'], item['url'], item['url_object_id'], item['create_time'], item['shoucang_nums'])
        insert_sql = "insert into jobbole_article(title,create_time,url,url_object_id,image_url,image_path,comment_nums,shoucang_nums,praise_nums,tag_lists,content) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(item['title'],item['create_time'],item['url'],item['url_object_id'],item['image_url'][0],item['image_path'],item['comment_nums'],item['shoucang_nums'],item['praise_nums'],item['tag_lists'],item['content'])

        cursor.execute(insert_sql)


    def handle_error(self,failure):
        print(failure)