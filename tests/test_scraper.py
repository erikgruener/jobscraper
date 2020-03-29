import unittest
import concurrent.futures
from bs4 import BeautifulSoup
from indeed.indeed_scraper import job_in_nogo
from indeed.indeed_scraper import download_pages_soup
from indeed.indeed_scraper import get_page_count

'''
To run the test call from the jobscraper folder
$python -m unittest tests/test_scraper.py -v

To run coverage test run
$coverage run -m unittest tests/test_scraper.py -v
$coverage report --omit=*/lib/*
'''

class TestScraper(unittest.TestCase):

    def test_nogo_jobtitle(self):

        job_title = 'Head of Marketing'
        nogo_list = 'marketing'
        result = job_in_nogo(job_title,nogo_list)
        self.assertTrue(result)

    def test_website_scrape(self):
        
        website = 'https://de.indeed.com/jobs?q=werkstudent&l=Berlin'
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # submits the function to be executed and return a future object
            output = [executor.submit(download_pages_soup,website,page) for page in range(10)] 
        self.assertEqual(len(output),10,f"The lenghts is actually {len(output)}")

    def test_get_page_count(self):
        source_text = open("tests/example_soup.txt","r")
        soup = BeautifulSoup(source_text, 'lxml')
        source_text.close()
        number = get_page_count(soup)
        self.assertEqual(number,142)

if __name__ == '__main__':
    unittest.main()
