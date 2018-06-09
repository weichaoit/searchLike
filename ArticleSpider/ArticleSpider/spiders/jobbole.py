# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobBoleArticleItem,ArticleItemLoader
from ArticleSpider.utils.common import get_md5
from scrapy.loader import ItemLoader


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        '''
        1.获取文章列表的文章url,让scrapy下载解析
        2.获取下一个页面url 并让scrapy进行下载
        :param response: 
        :return: 
        '''
        # 当前页面所有url
        all_post_nodes = response.xpath('//div[contains(@class,"floated-thumb")]/div[@class="post-thumb"]//a')
        for post_node in all_post_nodes:
            image_url = post_node.xpath('img//@src').extract()[0]
            post_url = post_node.xpath('@href').extract()[0]
            yield Request(url=parse.urljoin(response.url,post_url),meta={'image_url':image_url},callback=self.parse_detail)

        # 下一页的url
        next_page = response.xpath('//a[contains(@class,"next page-numbers")]//@href').extract()
        if next_page:
            yield Request(url=parse.urljoin(response.url,next_page),callback=self.parse)


    def parse_detail(self,response):
        article_item = JobBoleArticleItem()
        '''
        处理文章内容
        :param response: 
        :return: 
        '''
        # 文章封面图
        image_url = response.meta.get('image_url','')
        # # 标题
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]
        # # 创建时间
        # create_time = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace('·','').strip()
        # # 标签
        # tag_lists = response.xpath('//p[contains(@class,"entry-meta-hide-on-mobile")]/a/text()').extract()
        # tag_lists = [i for i in tag_lists if not i.strip().endswith('评论')]
        # tag_lists = ','.join(tag_lists)
        # # 点赞数
        # praise_nums = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()
        # if len(praise_nums) == 0:
        #     praise_nums = 0
        # else:
        #     praise_nums = praise_nums[0]
        #
        # # 收藏数
        # shoucang_nums = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract()[0]
        #
        # match_re = re.match(r'.*(\d+).*', shoucang_nums)
        # if match_re:
        #     shoucang_nums = match_re.group(1)
        # else:
        #     shoucang_nums = 0
        #
        # # 评论数
        # comment_nums = response.xpath('//span[contains(@class,"hide-on-480")]/text()').extract()[0]
        #
        # match_re = re.match(r'.*(\d+).*', comment_nums)
        # if match_re:
        #     comment_nums = match_re.group(1)
        # else:
        #     comment_nums = 0
        #
        # # 内容
        # content = response.xpath('//div[@class="entry"]').extract()[0]
        #
        # article_item['title'] = title
        # article_item['url'] = response.url
        # try:
        #     article_item['create_time'] = datetime.strptime(create_time,'%Y/%m/%d %H:%M:%S')
        # except Exception as e:
        #     article_item['create_time'] = datetime.now()
        # article_item['image_url'] = [image_url]
        # article_item['praise_nums'] = int(praise_nums)
        # article_item['shoucang_nums'] = int(shoucang_nums)
        # article_item['comment_nums'] = int(comment_nums)
        # article_item['content'] = content
        # article_item['url_object_id'] = get_md5(response.url)
        # article_item['tag_lists'] = tag_lists

        # 通过itemloader来加载实例
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(),response=response)
        # item_loader.add_css()
        # item_loader.add_xpath()
        item_loader.add_xpath('title','//div[@class="entry-header"]/h1/text()')
        item_loader.add_value('url',response.url)
        item_loader.add_value('url_object_id',get_md5(response.url))
        item_loader.add_xpath('create_time','//p[@class="entry-meta-hide-on-mobile"]/text()')
        item_loader.add_value('image_url',[image_url])
        item_loader.add_value('image_path',image_url)
        item_loader.add_xpath('praise_nums','//span[contains(@class,"vote-post-up")]/h10/text()')
        item_loader.add_xpath('comment_nums','//span[contains(@class,"hide-on-480")]/text()')
        item_loader.add_xpath('shoucang_nums','//span[contains(@class,"bookmark-btn")]/text()')
        item_loader.add_xpath('tag_lists','//p[contains(@class,"entry-meta-hide-on-mobile")]/a/text()')
        item_loader.add_xpath('content','//div[@class="entry"]')

        article_item = item_loader.load_item()

        yield article_item
