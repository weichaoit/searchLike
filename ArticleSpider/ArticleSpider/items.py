# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from datetime import datetime
from scrapy.loader.processors import MapCompose,TakeFirst,Join
from scrapy.loader import ItemLoader


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_conver(value):
    try:
        create_time = datetime.strptime(value, '%Y/%m/%d %H:%M:%S').date()
    except Exception as e:
        create_time = datetime.now().date()

    return create_time


def get_nums(value):
    # 处理带有数字的字符串
    match_re = re.match(r'.*(\d+).*', value)
    if match_re:
        nums = match_re.group(1)
    else:
        nums = 0

    return int(nums)


def tag_filter(value):
    # 去掉tag_list中的 评论
    if "评论" in value:
        return ''
    else:
        return value


def return_value(value):
    ''' 保持原值，不用取第一个值'''
    return value


class ArticleItemLoader(ItemLoader):
    # 重写，默认去列表第一个值
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_time = scrapy.Field(input_processor=MapCompose(date_conver))
    tag_lists = scrapy.Field(input_processor=MapCompose(tag_filter),output_processor=Join(','))
    praise_nums = scrapy.Field(input_processor=MapCompose(get_nums))
    shoucang_nums = scrapy.Field(input_processor=MapCompose(get_nums))
    comment_nums = scrapy.Field(input_processor=MapCompose(get_nums))
    content = scrapy.Field()
    image_url = scrapy.Field(output_processor=MapCompose(return_value))
    image_path = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()


