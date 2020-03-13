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

class AemoMapScraper(object):
    def __init__(self):
        super().__init__()

        # constants
        self.today = date.today().strftime('%d/%m/%Y')
        self.url_index = 'https://www.aemo.com.au/energy-systems/gas/gas-bulletin-board-gbb/interactive-map-gbb'
        self.output_dir = type(self).__name__ + '_' + time.strftime('%Y-%m-%d_%H,%M,%S', time.localtime()) + '/'

        self.tables = ['summary', 'pipelines', 'production', 'storage']
        self.filenames = {
            table: '{}{}_{}.csv'.format(self.output_dir, date.today().strftime('%Y-%m-%d'), table)
                for table in self.tables
        }

        self.data_headers = {
            'summary': ['StateShortName', 'GasDate', 'Demand', 'Supply'],
            'pipelines': ['ReferenceName', 'GasDate', 'Flow', 'Capacity', 'Utilisation'],
            'production': ['ReferenceName', 'GasDate', 'Flow', 'Capacity', 'Utilisation'],
            'storage': ['ReferenceName', 'GasDate', 'Flow', 'Balance', 'Utilisation']
        }

        # driver
        options = Options()
        # options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(300)
        # ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        self.wait = WebDriverWait(self.driver, 10)

        # logger
        LOGGER_FORMAT = '%(asctime)-15s  %(message)s'
        logging.basicConfig(level=logging.INFO, format=LOGGER_FORMAT)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialization finished.")

    def run(self):
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.logger.info('Files will be written in the directory: %s', self.output_dir)

        try:
            self.setup()

            for table in self.tables:
                self.scrape_table(table)

            self.logger.info('All done.')
        finally:
            self.driver.quit()
    
    def setup(self):
        self.driver.get(self.url_index)
        confirm_a = self.driver.find_element_by_xpath("//a[contains(text(), 'Confirm')]")
        confirm_a.click()

        iframe = self.driver.find_element_by_css_selector('div.iframe iframe')
        self.driver.switch_to.frame(iframe)
        try:
            agree_b = self.driver.find_element_by_css_selector(
                "button.wc-button.modal-button.primary")
            agree_b.click()
        except:
            self.logger.exception('Error getting agree_b.')

    def scrape_table(self, table):
        def write_rows(rows):
            with open(self.filenames[table], 'a') as f:
                writer = csv.writer(f)
                writer.writerows(row for row in rows if row)

        def parse_tr(tr):
            try:
                tds = tr.find_elements_by_tag_name('td')
                data = [td.text.strip().replace(',', '').replace('%', '') for td in tds]
                data.insert(1, self.today)
                return data
            except ValueError:
                self.logger.exception('valueerror')
                return []

        table_b_str = '#map-{}-button'.format(table)
        table_b = self.driver.find_element_by_css_selector(table_b_str.format(table))
        table_b.click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".active" + table_b_str)))
        trs = self.driver.find_elements_by_css_selector('tbody > tr:not(.filler)')
        rows = [parse_tr(tr) for tr in trs]
        write_rows([self.data_headers[table]])
        write_rows(rows)

if __name__ == "__main__":
    s = AemoMapScraper()
    s.run()
