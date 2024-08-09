import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PyPDF2 import PdfReader
import os
import time


class MpbCrawlerSpider(scrapy.Spider):
    name = "mpb_crawler"
    allowed_domains = ["www.bok.or.kr"]
    start_urls = ["https://www.bok.or.kr/portal/singl/newsData/list.do?pageIndex=&targetDepth=4&menuNo=200789&syncMenuChekKey=1&depthSubMain=&subMainAt=&searchCnd=1&searchKwd=&depth2=200038&depth3=201154&depth4=200789&date=&sdate=&edate=&sort=1&pageUnit=10"]

    def __init__(self):
        super(MpbCrawlerSpider, self).__init__(*args, **kwargs)
        headlessoptions = webdriver.Options()
        headlessoptions.add_argument('--headless')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=headlessoptions)

    def parse(self, response):
        self.driver.get(response.url)
        time.sleep(2)

        # achieve links for pdf downloads
        minutes_links = self.driver.find_elements(By.CSS_SELECTOR, 'div.bd-line li.bbsRowCls a.title')
        for link in minutes_links:
            minutes_url = 'https://www.bok.or.kr' + link.get_attribute('href')
            minutes_url
            yield scrapy.Request(minutes_url, callback=self.download_pdf)
        
        # moving to next page
        next_page = self.driver.find_element(By.XPATH, '//a[@rel="next"]')
        if next_page:
            next_page_url = next_page.get_attribute('href')
            yield scrapy.Request(next_page_url, callback=self.parse)

        response.css('div.abc::text').getall()

    def download_pdf(self, response):
        # PDF 파일을 저장
        pdf_path = os.path.join('pdfs', os.path.basename(response.url))
        with open(pdf_path, 'wb') as f:
            f.write(response.body)
        
        # PDF 파일 읽기
        reader = PdfReader(pdf_path)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        
        self.log(f'PDF 내용: {text}')

    def closed(self, reason):
        self.driver.quit()