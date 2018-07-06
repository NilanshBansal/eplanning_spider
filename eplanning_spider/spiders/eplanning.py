# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request,FormRequest

class EplanningSpider(scrapy.Spider):
    name = 'eplanning'
    # allowed_domains = ['eplanning.ie']
    start_urls = ['http://www.eplanning.ie/']

    def parse(self, response):
        urls = response.css('a::attr(href)').extract()
        for url in urls:
            if '#' == url:
                pass
            else:
                yield Request(url,callback=self.parse_application)
    
    def parse_application(self,response):
        app_url = response.css('span.glyphicon-inbox + a::attr(href)').extract_first()
        yield Request(response.urljoin(app_url),callback=self.parse_form)

    def parse_form(self,response):
        yield FormRequest.from_response(response,
                                        formdata={'RdoTimeLimit':'42'},
                                        dont_filter = True,
                                        formxpath = '(//form)[2]',
                                        callback = self.parse_pages)

    def parse_pages(self,response):
        pass                                   
