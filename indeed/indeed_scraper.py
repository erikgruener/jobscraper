from bs4 import BeautifulSoup
import requests
import csv
import sys
from argparse import ArgumentParser
import concurrent.futures

def download_pages_soup(website,page):
    source_text = requests.get(website+'&start='+str(page*10)).text
    soup = BeautifulSoup(source_text, 'lxml')
    return soup

def get_page_count(soup):
    page_count_text = soup.find('div',id='searchCountPages')
    page_count_text = page_count_text.text
    page_count_text = page_count_text.strip().split(' ')
    return int(int(page_count_text[3].replace('.',''))/16)
    
class Progressbar():

    def progress(self,count, total, status=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '=' * filled_len + '-' * (bar_len - filled_len)
        print("\r {} {} {}".format(bar, percents, status),end=" ")

def job_in_nogo(job_title,nogo_list):
	tags = job_title.lower().split()
	result = any([tag in nogo_list for tag in tags])
	return result

class Job_List:

    def __init__(self,job,loc,nogo_list,csv_writer,short):
        self.job = job
        self.loc = loc
        self.nogo_list = nogo_list
        self.csv_writer = csv_writer
        self.short=short

    def create_job_list(self):
        jobs_and_companies = []
        ProgressBar1 = Progressbar()
        ProgressBar2 = Progressbar()
        website = 'https://de.indeed.com/jobs?q='+self.job+'&l='+self.loc

        with concurrent.futures.ThreadPoolExecutor() as executor:
            output = [executor.submit(download_pages_soup,website,page) for page in range(self.page_count)] 
            for counter,fut in enumerate(concurrent.futures.as_completed(output)):
                ProgressBar1.progress(counter, self.page_count, status=f'Downloading {self.page_count} Webpages')
        print(" ")
        page_count = get_page_count(output[0])
        for idx,f in enumerate(output):
            ProgressBar2.progress(idx, self.page_count, status='Scraping webpages')
            soup = f.result()
            #Because sections can be missing like salary use try/except
            for y in soup.find_all('div',class_='jobsearch-SerpJobCard unifiedRow row result'):
                job_title = y.find('div', class_='title').a.text.strip("\n")
                company = y.find('span',class_='company').text.strip("\n")
                
                if (company.lower() in self.nogo_list or job_in_nogo(job_title,self.nogo_list)):
                    continue
                
                link = 'https://de.indeed.com'+y.find('div', class_='title').a.get('href')

                try:
                    salary = y.find('span',class_='salaryText').text.strip("\n")
                except:
                    salary=None

                if (self.short):
                    if (job_title,company) in jobs_and_companies:
                        continue
                    else:
                        jobs_and_companies.append((job_title,company))
                        self.csv_writer.writerow([job_title,company,salary,link])
                else:
                    self.csv_writer.writerow([job_title,company,salary,link])
            
def parse_options():
    parser = ArgumentParser()
    # You should always have -b or -d (or both) active.
    parser.add_argument("-j", "--job_title", required=False, default="werkstudent",
                        action="store_true",
                        help="What Job Title are you looking for.")
    parser.add_argument("-l", "--location", required=False,
                        default="Berlin", action="store_true",
                        help="City where you want to work.")
    parser.add_argument("-r", "--raw_data", required=False,
                        default="False", action="store_true",
                        help="Do you want all job including duplicates.")

    options = parser.parse_args()
    if not (options.job_title or options.location):
        print("You need to set the job -j you are looking for and a city -l")
        sys.exit(1)

    return options

if __name__ == "__main__":

    options = parse_options()
    job = options.job_title
    loc = options.location
    short = options.raw_data
    nogo_list = []#["marketing","audi","recruiting","lidl","personalwesen", "hr","human resources","social media"]

    csv_file = open("output_concurrent.csv", "w",newline='')
    csv_writer = csv.writer(csv_file,delimiter=',')
    csv_writer.writerow(['Job_Title','Company','Salary','Link'])

    Job_List = Job_List(job,loc,nogo_list,csv_writer, short)
    Job_List.create_job_list()
    csv_file.close()
