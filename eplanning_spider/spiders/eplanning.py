# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request,FormRequest

class EplanningSpider(scrapy.Spider):
    name = 'eplanning'
    # allowed_domains = ['eplanning.ie']
    start_urls = ['http://www.eplanning.ie/']

    def parse(self, response):
        urls = response.css('a::attr(href)').extract()
        for url in urls[0:10]:
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
        application_urls = response.css('td > a::attr(href)').extract()
        for url in application_urls:
            url = response.urljoin(url)
            yield Request(url,callback=self.parse_items)
        next_page_url =  response.css('li.PagedList-skipToNext > a::attr(href)').extract_first()  
        next_page_url = response.urljoin(next_page_url)
        yield Request(next_page_url,callback=self.parse_pages)
    def parse_items(self,response):
        agent_btn =  response.css('input[value="Agents"]::attr(style)').extract_first()
        if 'display: inline;  visibility: visible;' in agent_btn:
            name = response.css('th:contains("Name :") + td::text').extract_first()
            
            address_rows = int(response.css('tr > th:contains("Address :")::attr(rowspan)').extract_first())
            address_first_row_text = response.css('th:contains("Address :") + td::text').extract_first()
            address_rows_data_after_first = response.css('tr:contains("Address :") ~ tr>td::text').extract()[0:address_rows]
            
            complete_address = address_first_row_text 
            for text in address_rows_data_after_first:
                complete_address += " " + text.strip()
            
            phone = response.css('th:contains("Phone :") + td::text').extract_first()
            fax = response.css('th:contains("Fax :") + td::text').extract_first()
            e_mail = response.css('th:contains("e-mail :") + td > a::text').extract_first()
            url = response.url 

            yield {
                'name':name,
                'complete_address':complete_address,
                'phone':phone,
                'fax':fax,
                'e-mail':e_mail,
                'url':url
            }
                
        else:
            self.logger.info('Agent button not found on page, passing invalid url. ')
