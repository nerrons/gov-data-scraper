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

class Scraper(object):
    def __init__(self):
        super().__init__()

        # constants
        self.url_index = ''
        self.output_dir = type(self).__name__ + '_' + time.strftime('%Y-%m-%d_%H,%M,%S', time.localtime()) + '/'
        filename_stem = 'output'
        self.filename = self.output_dir + filename_stem + '.csv'

        self.DATE_FORMAT = '%Y/%m/%d'
        self.data_headers = [['col1', 'col2', 'col3', 'col4']]

        # important info
        self.stats = { 'stats1': 0 }

        # driver
        options = Options()
        # options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(3)
        self.driver.set_page_load_timeout(20)
        # ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        self.wait = WebDriverWait(self.driver, 3)

        # logger
        LOGGER_FORMAT = '%(asctime)-15s  %(message)s'
        logging.basicConfig(level=logging.INFO, format=LOGGER_FORMAT)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialization finished.")

    def run(self):
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.logger.info('Files will be written in the directory: %s', self.output_dir)

        try:
            self.write_rows(self.data_headers)

            self.scrape_1()

            self.logger.info('All done.')
        finally:
            self.driver.quit()

    def standardize_date(self, input_format):
        output_format = self.DATE_FORMAT
        def f(date_text):
            return datetime.strptime(date_text, input_format).strftime(output_format)
        return f
    
    def write_rows(self, rows):
        with open(self.filename, 'a') as f:
            writer = csv.writer(f)
            writer.writerows(row for row in rows if row)

    def scrape_1(self):

        def parse_tr(first_col):
            def f(tr):
                try:
                    tds = tr.find_elements_by_tag_name('td')
                    data_list = list(map(lambda td: td.text.strip(), tds))
                    col12 = list(map(self.standardize_date('%d/%m/%Y'), data_list[0:2]))
                    col3 = data_list[2]
                    return [first_col, col12[0], col12[1], col3]
                except ValueError:
                    return []
            return f

        self.driver.get(self.url_index)
        tbody_lists = [
            ('col1', self.driver.find_element_by_xpath("//h4[contains(text(), 'abc')]/..//tbody")),
            ('col2', self.driver.find_element_by_xpath("//h4[contains(text(), 'def')]/..//tbody"))
        ]
        tr_lists = list(map(lambda ttup: (ttup[0], ttup[1].find_elements_by_tag_name('tr')), tbody_lists))
        rows = list(map(lambda ttup: parse_tr(ttup[0])(ttup[1]), tr_lists))
        self.write_rows(rows)

if __name__ == "__main__":
    s = Scraper()
    s.run()
