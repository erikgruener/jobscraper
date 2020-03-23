#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import csv
import sys

def get_page_count(job,loc):
    source_text = requests.get('https://de.indeed.com/jobs?q='+job+'&l='+loc).text
    soup = BeautifulSoup(source_text, 'lxml')
    page_count_text = soup.find('div',id='searchCountPages')
    page_count_text = page_count_text.text
    page_count_text = page_count_text.strip().split(' ')
    return int(int(page_count_text[3].replace('.',''))/20)

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def create_job_list(page_count,job,loc,nogo_list,csv_writer):
    for page in range(page_count):
        progress(page, page_count, status=f'Downloading Jobs from {page_count} pages')
        source_text = requests.get('https://de.indeed.com/jobs?q='+job+'&l='+loc+'&start='+str(page)).text
        soup = BeautifulSoup(source_text, 'lxml')

        #Because sections can be missing like salary use try/except
        for y in soup.find_all('div',class_='jobsearch-SerpJobCard unifiedRow row result'):
            job_title_works = y.find('div', class_='title').a.text
            company = y.find('span',class_='company').text
            if company in nogo_list:
                continue
            link = 'https://de.indeed.com'+y.find('div', class_='title').a.get('href')
            try:
                salary = y.find('span',class_='salaryText').text
            except:
                salary=None
            csv_writer.writerow([job_title_works,company,salary,link])

if __name__ == "__main__":

    job = 'Job'
    loc = 'City'
    nogo_list = ['Firm1','Firm2']
    page_count = get_page_count(job,loc)

    csv_file = open('indeed_scrape.csv','w')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Job_Title','Company','Salary','Link'])

    create_job_list(page_count,job,loc,nogo_list,csv_writer)
    csv_file.close()