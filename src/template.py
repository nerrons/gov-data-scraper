import csv
from datetime import datetime, date, timedelta
import logging
import os
from pathlib import Path
import time
import pandas as pd
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

        ### constants
        # time
        self.now = time.localtime()
        self.DATE_FORMAT = '%Y/%m/%d'
        self.url_index = ''

        # paths
        output_dir = type(self).__name__ + '_' + time.strftime('%Y-%m-%d_%H,%M,%S', self.now)
        self.output_dir_path = (Path.cwd() / 'output' / output_dir).resolve()
        file_name_stem = 'output'
        file_name = file_name_stem + '.csv'
        self.file_path = self.output_dir_path / file_name

        ### data
        self.cols = ['col1', 'col2', 'col3', 'col4']
        self.df = pd.DataFrame(columns=self.cols)

        ### driver
        options = Options()
        # options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(60)
        # ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        self.wait = WebDriverWait(self.driver, 10)

        ### logger
        LOGGER_FORMAT = '%(asctime)-15s  %(message)s'
        logging.basicConfig(level=logging.INFO, format=LOGGER_FORMAT)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialization finished.")

    def run(self):
        self.output_dir_path.mkdir(parents=True, exist_ok=True)
        self.logger.info('Files will be written in the directory: %s', str(self.output_dir_path))

        try:
            self.scrape_1()

            self.logger.info('All done.')
        finally:
            self.driver.quit()

    # helper functions to make code more readable
    def css(self, selector, parent=None):
        if not parent: parent = self.driver
        return parent.find_element_by_css_selector(selector)
    def allcss(self, selector, parent=None):
        if not parent: parent = self.driver
        return parent.find_elements_by_css_selector(selector)
    def xpath(self, selector, parent=None):
        if not parent: parent = self.driver
        return parent.find_element_by_xpath(selector)
    def allxpath(self, selector, parent=None):
        if not parent: parent = self.driver
        return parent.find_elements_by_xpath(selector)

    def standardize_date(self, input_format):
        output_format = self.DATE_FORMAT
        def f(date_text):
            return datetime.strptime(date_text, input_format).strftime(output_format)
        return f
    
    def write_rows(self, rows):
        for row in rows:
            self.df = self.df.append(pd.Series(row, index=self.df.columns), ignore_index=True)
        with self.file_path.open('a') as f:
            writer = csv.writer(f)
            writer.writerows(row for row in rows if row)

    def scrape_1(self):
        css, allcss, xpath, allxpath = self.css, self.allcss, self.xpath, self.allxpath # pylint: disable=unused-variable

        def parse_tr(prefix_cols):
            def f(tr):
                try:
                    tds = tr.find_elements_by_tag_name('td')
                    data_list = [td.text.strip() for td in tds]
                    # data_list[2] = list(map(self.standardize_date('%d/%m/%Y'), data_list[0:2]))
                    return prefix_cols + data_list
                except ValueError:
                    return []
            return f

        self.driver.get(self.url_index)
        tbody_tups = [
            ('sheet1', xpath("//*[contains(text(), 'abc')]/..//tbody")),
            ('sheet2', css("table > tbody"))
        ]
        trs_tups = [ (ttup[0], allcss('tr', ttup[1])) for ttup in tbody_tups ]
        rows = sum([ [ parse_tr(ttup[0])(tr) for tr in ttup[1] ] for ttup in trs_tups], [])
        self.write_rows(rows)

if __name__ == "__main__":
    scraper = Scraper()
    scraper.run()
