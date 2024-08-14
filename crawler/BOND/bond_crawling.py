from bs4 import BeautifulSoup
import requests
import time
import re
from requests import get
from urllib import request
from PyPDF2 import PdfReader
import os
import csv
from pykospacing import Spacing
import os.path
import shutil
from tika import parser
from datetime import datetime


# 1
today = "2024-08-11"

target_day = "2024-05-11"

url = f"https://finance.naver.com/research/debenture_list.naver?keyword=&brokerCode=&searchType=writeDate&writeFromDate={target_day}&writeToDate={today}&x=0&y=0&page=1"
temp_url = "https://finance.naver.com/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36', 
    'Referer': 'https://www.naver.com/'
    }

# 2
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

last_page = soup.select_one('td.pgRR>a').attrs['href']
temp = f"/research/debenture_list.naver?keyword=&brokerCode=&searchType=writeDate&writeFromDate={target_day}&writeToDate={today}&x=0&y=0&page="
pages = int(last_page.replace(temp,''))

#3
for page in range(1, pages+1):
    page_url = f"https://finance.naver.com/research/debenture_list.naver?keyword=&brokerCode=&searchType=writeDate&writeFromDate={target_day}&writeToDate={today}&x=0&y=0&page={page}"

    headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36', 
            'Referer': 'https://www.naver.com/'
        }

    response = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    reports = soup.select('table.type_1 tr')
    normal_page = "https://finance.naver.com/research/"

    print(f"{page} 번 페이지 진행중입니다")

    for report in reports:
        report_link = report.select("a")
        if report_link == []:
            pass
        else:
            report_page = normal_page + report_link[0].attrs['href']  # report_page : 각 레포트별 페이지 url이 반복을 돌면서 하나씩 들어오는 변수
        
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36', 
                'Referer': 'https://www.naver.com/'
                }
            response = requests.get(report_page, headers=headers)
            print(report_page)
            soup = BeautifulSoup(response.text, 'html.parser')

            report_info = soup.select_one('p.source').text
            report_info = report_info.replace("\n",'')
            report_info = report_info.replace("\t",'')
            report_info = report_info.split("|")
            cop_name = report_info[0]
            published_date = report_info[1]
            
            # 리포트 제목 추출
            report_title = soup.select_one('th.view_sbj').text
            title = report_title.replace("\n",'')
            title = title.replace("\t",'')
            title = title.split(cop_name)
            title = title[0]
            title = title.replace('  ','') 
            for idx in range(len(title)): #공백제거
                if title[idx] != ' ':
                    target_idx = idx
            title = title[:target_idx+1]
            new_title = ''
            for i in title:
                if i == "/":
                    new_title += "_"
                else:
                    new_title += i
            title = new_title
            print(f"리서치 제목 : {title}")
            
            # 리포트 전체 내용 추출(PDF 포함)
            content = soup.select_one("td.view_cnt").text
            content = content.replace('\n','')

            # PDF 추출
            pdf_name = soup.select("a.con_link")[1].text
            if pdf_name == '':
                print("PDF 파일이 없습니다 이 경우엔 수집하지 않습니다")
                pass
            else:
                print("PDF 파일이 존재 합니다")
                content = content.split(pdf_name)  # 내용과 PDF 분리
                content = content[0]
                pdf_link = soup.select_one("a.con_link").attrs['href'] # PDF 다운로드 링크
                pdf_name = soup.select("a.con_link")[1].text # PDF 파일 이름  
                if "/" in pdf_name:
                    pdf_name = pdf_name.replace('/','_')
                pdf_name_2 = soup.select("a.con_link")[1].text[:-4]  # .pdf 확장자명 제거
                pdf = pdf_name
                # PDF 저장
                with open(pdf, "wb") as file:   # open in binary mode
                    response = get(pdf_link)  # get request
                    time.sleep(1)
                    file.write(response.content)

                # PDF 텍스트 추출
                PDF_FILE_PATH = pdf
                parsed = parser.from_file(PDF_FILE_PATH)
                text = parsed['content']
                print(text)
                
                if text is None:
                    print("pdf 파일을 읽을 수 없습니다")
                else:
                    str_text = text
                    new_str = re.sub("\n", "", str_text)
                    new_str = re.sub(" ", "", new_str)

                    spacing = Spacing()
                    kospacing_result = spacing(new_str)

                    directory = f'./dataset/{published_date}'

                    if os.path.isdir(directory):
                        print(directory)
                        print("저장경로 있습니다")
                        time.sleep(1)
                    else:
                        print("저장경로가 없습니다")
                        current_path = os.getcwd()
                        os.mkdir(directory)
                        time.sleep(2)
                        if os.path.isdir(directory):
                            print("저장경로 생성하였습니다")
                        else:
                            print("저장경로 생성 실패하였습니다")

                    # CSV 파일에 데이터 저장
                    csv_file_path = f'{directory}/{title}_{cop_name}_{published_date}.csv'
                    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                        csvwriter = csv.writer(csvfile)
                        csvwriter.writerow(['제목', '요약', '내용'])  # CSV 헤더
                        csvwriter.writerow([title, content, kospacing_result])  # CSV 데이터
                    
                    time.sleep(1)

                # 파일 삭제
                remove_file_path = PDF_FILE_PATH # 제거할 파일
                os.remove(remove_file_path)