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

class TomCityScraper(object):
    def __init__(self):
        super().__init__()

        # constants
        self.url_prefix = 'https://www.tomtom.com/en_gb/traffic-index/'
        self.url_postfix = '-traffic'
        self.output_dir = type(self).__name__ + '_' + time.strftime('%Y-%m-%d_%H,%M,%S', time.localtime()) + '/'
        filename_stem = 'output'
        self.filename = self.output_dir + filename_stem + '.csv'

        self.DATE_FORMAT = '%Y/%m/%d'
        # self.data_headers = [['col1', 'col2', 'col3', 'col4']]

        # important info
        self.stats = { 'stats1': 0 }

        # driver
        options = Options()
        # options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(60)
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
            # self.write_rows(self.data_headers)

            self.scrape_city('beijing')
            self.logger.info('All done.')
        finally:
            self.driver.quit()

    def standardize_date(self, input_format):
        output_format = self.DATE_FORMAT
        def f(date_text):
            return datetime.strptime(date_text, input_format).strftime(output_format)
        return f
    
    def write_row(self, row):
        self.logger.info(row)
        # with open(self.filename, 'a') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(row)

    def scrape_city(self, city):
        def find(selector):
            return self.driver.find_element_by_css_selector(selector).text.replace('\n', '')
        
        self.driver.get(self.url_prefix + city + self.url_postfix)
        localtime = find('span.CityLocalTime').split(':')
        localtime = ' '.join([localtime[0], localtime[1][-2:]])
        temperature = find('span.CityWeather__temperature')
        live_number = find('div.live-number:nth-child(2)')
        delta_label = find('.CityLiveTraffic__delta-label')
        sign = '-' if 'less' in delta_label else '+'
        delta_value = sign + find('span.Delta__value')
        jams_count = find('li.CityLiveTraffic__jams-stat:nth-child(1) > div.CityLiveTraffic__jams-info-value')
        jams_length = find('li.CityLiveTraffic__jams-stat:nth-child(2) > div.CityLiveTraffic__jams-info-value')
        row = [localtime, temperature, live_number, delta_value, jams_count, jams_length]
        self.write_row(row)

if __name__ == "__main__":
    s = TomCityScraper()
    s.run()
