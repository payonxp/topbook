# -*- coding: utf-8 -*-
from scrapy import Request
from scrapy.spiders import Spider
from topbook.items import TopbookItem
from pymongo import MongoClient

class DoubanBookTop250Spider(Spider):
    name = 'topbook'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    }

    mongoClient = MongoClient('115.28.101.55', 27017)
    db = mongoClient['test']
    urls = db.urls

    def start_requests(self):
        url = 'https://book.douban.com/top250'
        yield Request(url, headers=self.headers)

    def parse(self, response):
        if response.url.startswith('https://book.douban.com/top250'):
            books = response.xpath('//div[@class="indent"]/table')
            for book in books:
                try:
                    next_url = book.xpath(
                        './/div[@class="pl2"]/a/@href').extract()[0]
                    yield Request(next_url + 'comments', headers=self.headers)
                except Exception as err:
                    print(err)

            next_url = response.xpath('//div[@class="paginator"]/span[@class="next"]/a/@href').extract()[0]
            if self.checkUrl(next_url):
                yield Request(next_url, headers=self.headers)
        else:
            item = TopbookItem()
            book_name = response.xpath('//div[@id="content"]/h1/text()').extract()[0]
            comments = response.xpath('//div[@id="comments"]/ul/li')
            for comment in comments:
                try:
                    item['book_name'] = book_name
                    item['author'] = comment.xpath(
                        './/div[@class="comment"]/h3/span[@class="comment-info"]/a/text()').extract()[0]
                    item['time'] = comment.xpath(
                        './/div[@class="comment"]/h3/span[@class="comment-info"]/span/text()').extract()[0]
                    item['vote'] = comment.xpath(
                        './/div[@class="comment"]/h3/span[@class="comment-vote"]/span/text()').extract()[0]
                    item['content'] = comment.xpath(
                        './/div[@class="comment"]/p/text()').extract()[0]
                except Exception as err:
                    print(err)
                yield item

            next_urls = response.xpath('//a[@class="page-btn"]/@href').extract()
            pos = response.url.find("hot?p=")
            if pos != -1:
                url = response.url[:pos]
                if self.checkUrl(url + next_urls[len(next_urls) - 1]):
                    yield Request(url + next_urls[len(next_urls) - 1], headers=self.headers)
            else:
                if self.checkUrl(response.url + next_urls[len(next_urls) - 1]):
                    yield Request(response.url + next_urls[len(next_urls) - 1], headers=self.headers)

    def checkUrl(self, url):
        try:
            u = self.urls.find_one({"url": url})
            if u is None:
                self.urls.insert_one({"url": url})
                return True
            else:
                return False
        except Exception as err:
            print(err)
            return True