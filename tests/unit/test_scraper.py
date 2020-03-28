import unittest
from indeed_scraper import job_in_nogo
import concurrent.futures
from indeed_scraper import download_pages_soup
from indeed_scraper import get_page_count

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
        get_page_count('werkstudent','Berlin')
        pass

if __name__ == '__main__':
    unittest.main()
