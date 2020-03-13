import csv
from datetime import datetime, date, timedelta
import logging
import os
from pathlib import Path
import time
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, 
    StaleElementReferenceException, 
    ElementNotInteractableException,
    TimeoutException
)

class RimIntelScraper(object):
    def __init__(self):
        super().__init__()

        # constants
        self.url_index = 'https://eng.rim-intelligence.co.jp/news/topics/nuclear/'
        self.output_dir = type(self).__name__ + '_' + time.strftime('%Y-%m-%d_%H,%M,%S', time.localtime()) + '/'
        filename_stem = 'output'
        self.filename = self.output_dir + filename_stem + '.csv'

        self.DATE_FORMAT = '%Y/%m/%d'
        self.data_headers = [['facility', 'start_date', 'end_date', 'notes']]

        self.username = 'tony.zhu@glencore.com.sg'
        self.password = 'G856mT5'

        # important info
        self.stats = { 'stats1': 0 }

        # driver
        options = Options()
        # options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(120)
        # ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        self.wait = WebDriverWait(self.driver, 10)

        # logger
        LOGGER_FORMAT = '%(asctime)-15s  %(message)s'
        logging.basicConfig(level=logging.INFO, format=LOGGER_FORMAT)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialization finished.")

    def run(self):
        # Make directories for output
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.logger.info('Files will be written in the directory: %s', self.output_dir)

        # Log in with credentials
        self.login()

        try:
            self.write_rows(self.data_headers)

            self.scrape_tar()

            self.logger.info('All done.')
        finally:
            self.driver.quit()

    def standardize_date(self, input_format):
        output_format = self.DATE_FORMAT
        def f(date_text):
            if date_text == 'TBD': return '--'
            return datetime.strptime(date_text, input_format).strftime(output_format)
        return f

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
    
    def write_rows(self, rows):
        with open(self.filename, 'a') as f:
            writer = csv.writer(f)
            writer.writerows(row for row in rows if row)

    # works like a charm
    def login(self):
        self.driver.get(self.url_index)
        login_button = self.driver.find_element_by_xpath("//a[contains(text(), 'Log in')]")
        login_button.click()
        username_field = self.driver.find_element_by_id('username')
        username_field.send_keys(self.username)
        password_field = self.driver.find_element_by_id('password')
        password_field.send_keys(self.password)
        submit_button = self.driver.find_element_by_id('submit')
        submit_button.click()

    def scrape_tar(self):

        def parse_tr(facility):
            if 'Sendai' in facility or 'Genkai' in facility:
                regex = r'(\d+/[A-Z][a-z]+/\d+) to (\d+/[A-Z][a-z]+/\d+)'
            elif 'Ikata' in facility:
                regex = r'0:00 on (\d+/[A-Z][a-z]+/\d+) to (\w+)'
            elif 'Takahama' in facility:
                self.logger.info('Having %s', facility)
                regex = r'(\d+/[A-Z][a-z]+\s?/\d+)\s?-\s?(\d+/[A-Z][a-z]+\s?/\d+)'
            else:
                self.logger.info('Going %s', facility)
                regex = r'(?:(\d+/[A-Z][a-z]+\s?/\d+)\s?-\s?(\d+/[A-Z][a-z]+\s?/\d+))|(?:(\d+/[A-Z][a-z]+\s?/\d+)\s?-\s?to\s?\d\d:\d\d\s?on\s?(\d+/[A-Z][a-z]+\s?/\d+))'

            def f(tr):
                try:
                    tds = tr.find_elements_by_tag_name('td')
                    # status = tds[6].find_element_by_tag_name('p').get_attribute('innerText')
                    notes = self.full2half(tds[7].find_element_by_tag_name('p').get_attribute('innerText')).replace('\n', ' | ')
                    checkup_dates_str = list(map(lambda s: list(map(lambda x: x.replace(' ', ''), s)), re.findall(regex, notes)))
                    if len(checkup_dates_str[0]) == 4:
                        checkup_dates_str = list(map(lambda tup: list(filter(None, tup)), checkup_dates_str))
                    self.logger.info('checkup_dates_str %s', checkup_dates_str)
                    checkup_dates = list(map(lambda tup: list(map(self.standardize_date('%d/%b/%y'), tup)), checkup_dates_str))
                    self.logger.info('checkup_dates: %s', checkup_dates)
                    return [[facility, dates[0], dates[1], notes] for dates in checkup_dates]
                except ValueError:
                    return []
            return f

        tr_lists = [
            ('Sendai No. 1', self.driver.find_element_by_xpath("//p[contains(span, 'Sendai')]/../..")),
            ('Sendai No. 2', self.driver.find_element_by_xpath("//p[contains(span, 'Sendai')]/../..//following-sibling::tr")),
            ('Genkai No. 3', self.driver.find_element_by_xpath("//p[contains(span, 'Genkai')]/../..")),
            ('Genkai No. 4', self.driver.find_element_by_xpath("//p[contains(span, 'Genkai')]/../..//following-sibling::tr")),
            ('Ikata No. 3', self.driver.find_element_by_xpath("//p[contains(span, 'Ikata')]/../..")),
            ('Takahama No. 3', self.driver.find_elements_by_xpath("//p[contains(span, 'Takahama')]/../..//following-sibling::tr")[1]),
            ('Takahama No. 4', self.driver.find_elements_by_xpath("//p[contains(span, 'Takahama')]/../..//following-sibling::tr")[2]),
            ('Ohi No. 3', self.driver.find_element_by_xpath("//span[contains(span, 'Ohi')]/../../..")),
            ('Ohi No. 4', self.driver.find_element_by_xpath("//span[contains(span, 'Ohi')]/../../..//following-sibling::tr"))
        ]
        # need to use a sum here, since a tr fed to parse_tr will retern a list of lists
        # (e.g. multiple rows to be written to the result)
        rows = sum(list(map(lambda ttup: parse_tr(ttup[0])(ttup[1]), tr_lists)), [])
        self.write_rows(rows)

if __name__ == "__main__":
    s = RimIntelScraper()
    s.run()
