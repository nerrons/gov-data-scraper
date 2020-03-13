import csv
from datetime import datetime, date, timedelta
import logging
import os
from pathlib import Path
import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, 
    StaleElementReferenceException, 
    ElementNotInteractableException,
    TimeoutException
)

class EnergyGovAuScraper(object):
    def __init__(self):
        super().__init__()

        # constants
        self.url_index = 'https://www.energy.gov.au/publications/australian-petroleum-statistics-2019'
        self.output_dir = type(self).__name__ + '_' + time.strftime('%Y-%m-%d_%H,%M,%S', time.localtime()) + '/'
        filename_stem = 'output'
        self.filename = self.output_dir + filename_stem + '.csv'

        # important info
        self.links = []
        self.stats = { 'stats1': 0 }

        # driver
        options = Options()
        # options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(60)
        # ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        self.wait = WebDriverWait(self.driver, 20)

        # logger
        LOGGER_FORMAT = '%(asctime)-15s  %(message)s'
        logging.basicConfig(level=logging.INFO, format=LOGGER_FORMAT)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialization finished.")

    def run(self):
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.logger.info('Files will be written in the directory: %s', self.output_dir)

        try:
            self.gen_links()
            for link in self.links:
                self.download(link)

            self.logger.info('All done.')
        finally:
            self.driver.quit()
    
    def write_rows(self, rows):
        with open(self.filename, 'a') as f:
            writer = csv.writer(f)
            writer.writerows(row for row in rows if row)

    def gen_links(self):
        self.driver.get(self.url_index)
        a_list = self.driver.find_elements_by_css_selector('a[href*=".xlsx"')
        self.links = list(map(lambda a: a.get_attribute('href'), a_list))
        self.logger.info("Links: %s", self.links)

    def download(self, link):
        filename = link.rpartition('/')[2]
        response = requests.get(link)
        with open(self.output_dir + filename, 'wb') as f:
            f.write(response.content)

if __name__ == "__main__":
    s = EnergyGovAuScraper()
    s.run()
