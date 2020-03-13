import csv
from datetime import datetime, date, timedelta
import logging
import os
import re
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

class PowerScraper(object):
    def __init__(self):
        super().__init__()

        # constants
        self.now = time.localtime()
        self.urls = {
            'genkai' :'http://www.kyuden.co.jp/php/nuclear/genkai/g_power.php',
            'sendai': 'http://www.kyuden.co.jp/php/nuclear/sendai/s_power.php'
        }
        self.output_dir = type(self).__name__ + '_' + time.strftime('%Y-%m-%d_%H,%M,%S', self.now) + '/'
        filename_stem = 'output'
        self.filename = self.output_dir + filename_stem + '.csv'

        self.DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

        # data frame
        self.df = pd.DataFrame(columns=['update_time', 'facility', 'status'])

        # driver
        options = Options()
        # options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(600)
        self.driver.implicitly_wait(20)
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
            self.scrape_kyuden('genkai')
            self.scrape_kyuden('sendai')

            self.logger.info('All done.')
            print(self.df)
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

    def full2half(self, s):
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

    def write_rows(self, rows):
        for row in rows:
            self.df = self.df.append(pd.Series(row, index=self.df.columns), ignore_index=True)
        with open(self.filename, 'a') as f:
            writer = csv.writer(f)
            writer.writerows(row for row in rows if row)

    def scrape_kyuden(self, facility):
        css = self.css
        allcss = self.allcss

        def parse_tr(prefix_cols):
            def f(tr):
                try:
                    data = css('td', tr).text.strip()
                    unit = self.full2half(css('th', tr).text[0])
                    return prefix_cols + ['{} #{}'.format(facility, unit), data]
                except ValueError:
                    return []
            return f

        self.driver.get(self.urls[facility])
        last_update_str = self.xpath('//*[@id="lastupdate" and contains(text(), "月")]').text
        self.logger.info(last_update_str)
        last_update = self.standardize_date('%Y年%m月%d日 %H時%M分')(last_update_str)
        tbody_tups = [ ([last_update], tbody)
                for tbody in allcss('div.nuclear__dataArea > table.newclear__hatsudenki > tbody') ]
        trs_tups = [ (ttup[0], allcss('tr', ttup[1])) for ttup in tbody_tups ]
        rows = sum([ [ parse_tr(ttup[0])(tr) for tr in ttup[1] ] for ttup in trs_tups], [])
        self.write_rows(rows)

if __name__ == "__main__":
    s = PowerScraper()
    s.run()
