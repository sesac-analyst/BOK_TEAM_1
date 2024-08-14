import scrapy
from PyPDF2 import PdfReader
from io import BytesIO
import os
import time
import re


class MpbCrawlerSpider(scrapy.Spider):
    name = "mpb_crawler"
    allowed_domains = ["www.bok.or.kr"]

    def start_requests(self):
        base_url = 'https://www.bok.or.kr/portal/singl/newsData/listCont.do'
        params = {
            'targetDepth': 4,
            'menuNo': 200789,
            'syncMenuChekKey': 1,
            'depthSubMain': '',
            'subMainAt': '',
            'searchCnd': 1,
            'searchKwd': '',
            'depth2': 200038,
            'depth3': 201154,
            'depth4': 200789,
        }

        for page_index in range(1, 4): # 21로 해야함
            params['pageIndex'] = page_index
            url = f"{base_url}?{'&'.join([f'{key}={value}' for key, value in params.items()])}"
            yield scrapy.Request(url=url, callback=self.parse)
        

    def parse(self, response):
        # achieve links for pdf downloads

        # links for each articles in the list
        for news_item in response.css('li.bbsRowCls'):
            news_link = news_item.css('a::attr(href)').get()
            title = news_item.css('a::text').get().strip()
            if news_link:
                yield response.follow(news_link, self.download_pdf, meta={'title':title})

    def download_pdf(self, response):
        base_url = 'https://www.bok.or.kr'
        pdf_links = response.css('a.file::attr(href)').getall()
        title = response.meta.get('title')

        if len(pdf_links) > 1:
            pdf_url = base_url + pdf_links[1]
            yield scrapy.Request(pdf_url, callback=self.parse_pdf, meta={'title': title})

    def parse_pdf(self, response):
        try:
            # PDF 파일 읽기
            pdf_reader = PdfReader(BytesIO(response.body))

            # 제목에서 날짜 추출
            date_match = re.search(r'\((\d{4}.\d{2}.\d{2})\)', response.meta['title'])
            date = date_match.group(1) if date_match else None

            # 모든 페이지의 텍스트 추출
            text = ''
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
            print(text)

            yield {
                'date': date,
                'title': response.meta['title'],
                'text': text
            }

        except Exception as e:
            print(f"Error parsing PDF: {e}")