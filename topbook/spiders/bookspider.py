# -*- coding: utf-8 -*-
from scrapy import Request
from scrapy.spiders import Spider
from topbook.items import TopbookItem


class DoubanBookTop250Spider(Spider):
    name = 'topbook'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    }
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
                except Exception as err:
                    print(err)
                yield Request(next_url + 'comments', headers=self.headers)

            next_url = response.xpath('//div[@class="paginator"]/span[@class="next"]/a/@href').extract()[0]
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
            yield Request(response.url + next_urls[len(next_urls) - 1], headers=self.headers)

