import scrapy
from tika import parser
from io import BytesIO
import os
import time
import re
import requests


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
            title = news_item.css('a::text').getall()[1].strip()
            if news_link:
                yield response.follow(news_link, self.download_pdf, meta={'title':title})

    def download_pdf(self, response):
        base_url = 'https://www.bok.or.kr'
        pdf_links = response.css('a.file::attr(href)').getall()
        title = response.meta.get('title')

        if len(pdf_links) > 1:
            pdf_link = pdf_links[0] if 'pdf' in pdf_links[0] else pdf_links[1]
            pdf_url = base_url + pdf_link
            yield scrapy.Request(pdf_url, callback=self.parse_pdf, meta={'title': title})

    def parse_pdf(self, response):
        try:
            parsed = parser.from_buffer(response.body)
            text = parsed["content"]
            # 제목에서 날짜 추출 (기존 코드와 동일)
            date_match = re.search(r'\((\d{4}\.\d{1,2}\.\d{1,2})\)', response.meta['title'])
            date = date_match.group(1) if date_match else None
            title = response.meta['title']

            # section2 (위원 토의내용) 추출
            discussion_pattern = r"\(２\) 위원 토의내용\n(.*?)\n\(３\) 심의결과"
            discussion_content = re.search(discussion_pattern, text, re.DOTALL)
            if discussion_content:
                discussion_text = discussion_content.group(1).strip()
            else:
                print("위원 토의내용을 찾을 수 없습니다.")

            # section3 (심의결과) 추출
            decision_pattern = r"\(３\) 심의결과(.*)"
            decision_content = re.search(decision_pattern, text, re.DOTALL)
            if decision_content:
                decision_text = decision_content.group(1).strip()
            else:
                print("심의결과를 찾을 수 없습니다.")

            if text:
                yield {
                    'date': date,
                    'title': title,
                    'content': text,
                    'discussion': discussion_text,
                    'decision': decision_text,
                    'link': response.url
                }
            else:
                print("pdf 파일을 읽을 수 없습니다")
    
        except Exception as e:
            print(f"Error parsing PDF: {e}")