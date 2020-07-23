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
    def __init__(self, cols):
        '''pass in the columns of the csv'''

        super().__init__()

        ### constants
        # time
        self.now = time.localtime()
        self.DATE_FORMAT = '%Y/%m/%d'

        # paths
        output_dir = type(self).__name__ + '_' + time.strftime('%Y-%m-%d_%H,%M,%S', self.now)
        self.output_dir_path = (Path.cwd() / 'output' / output_dir).resolve()
        file_name_stem = 'output'
        file_name = file_name_stem + '.csv'
        self.file_path = self.output_dir_path / file_name

        # data
        self.cols = cols
        self.df = pd.DataFrame(columns=self.cols)

        # driver
        options = Options()
        # options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(20)
        self.driver.set_page_load_timeout(600)
        # ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        self.wait = WebDriverWait(self.driver, 20)

        # logger
        LOGGER_FORMAT = '%(asctime)-15s  %(message)s'
        logging.basicConfig(level=logging.INFO, format=LOGGER_FORMAT)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialization finished.")

    def make_dir(self):
        self.output_dir_path.mkdir(parents=True, exist_ok=True)
        self.logger.info('Files will be written in the directory: %s', str(self.output_dir_path))

    def scrape(self, proc):
        '''Scrape according to proc and return the DataFrame.'''
        self.make_dir()
        try:
            proc()
            self.logger.info('All done.')
        finally:
            self.driver.quit()

        return self.df

    # helper functions to make code more concise
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
    def shorter_find(self):
        return (self.css, self.allcss, self.xpath, self.allxpath)

    @staticmethod
    def full2half(s):
        # ref:https://segmentfault.com/a/1190000006197218
        n = []
        for char in s:
            num = ord(char)
            if num == 0x3000:
                num = 32
            elif 0xFF01 <= num <= 0xFF5E:
                num -= 0xfee0
            num = chr(num)
            n.append(num)
        return ''.join(n)

    def standardize_date(self, input_format):
        output_format = self.DATE_FORMAT
        def f(date_text):
            return datetime.strptime(date_text, input_format).strftime(output_format)
        return f

    def write_rows(self, rows, write_csv=False):
        for row in rows:
            self.df = self.df.append(pd.Series(row, index=self.df.columns), ignore_index=True)
        if write_csv:
            with self.file_path.open('a') as f:
                writer = csv.writer(f)
                writer.writerows(row for row in rows if row)
