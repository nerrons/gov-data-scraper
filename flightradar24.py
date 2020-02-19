import csv
from datetime import datetime, date, timedelta
import time
import os
from pathlib import Path
import logging
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

class AirportScraper(object):
    def __init__(self, days_ago=0, fetch_china=True, additional_airports=[]):
        super().__init__()

        # constants
        self.url_prefix = 'https://www.flightradar24.com/data/airports/'
        self.url_postfix = '/departures'

        self.target_day = (date.today() - timedelta(days=days_ago)).strftime('%b %d')
        self.target_day_str = (date.today() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        self.prev_day = date.today() - timedelta(days=days_ago + 1)
        self.next_day = date.today() - timedelta(days=days_ago - 1)

        self.output_dir = 'flightradar24_' + time.strftime('%Y-%m-%d_%H,%M,%S', time.localtime()) + '/'
        filename_stem = self.target_day_str + '_'
        self.filename_flights = self.output_dir + filename_stem + 'flights.csv'
        self.filename_stats = self.output_dir + filename_stem + 'stats.csv'

        # important info
        self.fetch_china = fetch_china
        self.airport_codes_list = additional_airports
        self.stats = { 'total_num_of_flights': 0 }

        # driver
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(100)
        #ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        self.wait = WebDriverWait(self.driver, 15)

        # logger
        FORMAT = '%(asctime)-15s  %(message)s'
        logging.basicConfig(level=logging.INFO, format=FORMAT)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialization finished.")

    def run(self):
        # make dir
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.logger.info('Files will be written in the directory: %s', self.output_dir)

        # scrape everything
        try:
            if self.fetch_china:
                self.gen_airport_list()
            while self.airport_codes_list:
                self.scrape_airport(self.airport_codes_list[0])
                self.airport_codes_list.pop(0)

            self.logger.info('Total flights: %s', self.stats['total_num_of_flights'])
        finally:
            self.driver.quit()

    def gen_airport_list(self):
        self.driver.get(self.url_prefix + 'china')
        table_rows = (self.driver
                .find_element_by_css_selector('#tbl-datatable > tbody')
                .find_elements_by_css_selector('tr:not(.header)')[1:]
            )
        self.airport_codes_list.extend(list(map(
                lambda x: (x
                        .find_element_by_css_selector('td:nth-child(2) > a')
                        .get_attribute('href')
                        .rpartition('/')[2]
                    ),
                table_rows)))
        self.logger.info('Airport list: %s', list(map(lambda x: x.upper(), self.airport_codes_list)))

    def write_flight_rows(self, rows):
        with open(self.filename_flights, 'a') as f:
            writer = csv.writer(f)
            writer.writerows([self.target_day_str] + row for row in rows if row)
    
    def write_stats_row(self, code, num):
        with open(self.filename_stats, 'a') as f:
            writer = csv.writer(f)
            writer.writerow([code.upper(), num])

    def scrape_airport(self, code):
        def parse_separator_date(text):
            return datetime.strptime('2020 ' + text, '%Y %A, %b %d').date()
        
        def expand(button_text, row_index, standard, retries):
            if (retries == 0): return

            try:
                button = self.driver.find_element_by_xpath("//*[contains(text(), '" + button_text + "')]")
            except NoSuchElementException:
                expand(button_text, row_index, standard, retries - 1)

            date_rows = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'row-date-separator')))
            edge_date = date_rows[row_index].text
            stuck_counter = 50
            while (stuck_counter > 0
                    and button.is_displayed()
                    and standard(parse_separator_date(edge_date))):
                try:
                    button.click()
                    last_len = len(date_rows)
                    date_rows = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'row-date-separator')))
                    edge_date = date_rows[row_index].text
                    if len(date_rows) == last_len: stuck_counter -= 1
                except StaleElementReferenceException:
                    continue
                except ElementNotInteractableException:
                    stuck_counter -= 1
                    continue
        
        def expand_upwards():
            expand('Load earlier flights', 0, lambda x: self.prev_day <= x, 5)
        def expand_downwards():
            expand('Load later flights', -1, lambda x: x <= self.next_day, 5)

        # get all today's flights and extract info
        def prepare_rows():
            # parse a tr and get details
            def parse_flight_row(row):
                departure_airport = code.upper()
                flight_time = row.find_element_by_css_selector('td.ng-binding').text
                flight_number = row.find_element_by_css_selector('td.cell-flight-number > a.notranslate.ng-binding').text
                airline = row.find_element_by_css_selector('td.cell-airline > a.notranslate.ng-binding').text.strip()
                dest_city = row.find_element_by_css_selector('td:nth-child(3) > div:nth-child(1) > span').text.strip()
                dest_airport = row.find_element_by_css_selector('td:nth-child(3) > div:nth-child(1) > a.notranslate.ng-binding').text[1:-1]
                status = row.find_element_by_css_selector('td:nth-child(7) > span.ng-binding').text
                return [departure_airport, flight_time, flight_number, dest_city, dest_airport, airline, status]

            today_flights = self.driver.find_elements_by_css_selector("tr[data-date*='" + self.target_day + "']")
            return list(map(parse_flight_row, today_flights))

        def test_have_data():
            try:
                sorry = self.driver.find_element_by_xpath("//*[contains(text(), 'have any information about flights for this airport')]")
                if sorry and sorry.is_displayed(): raise ValueError
            except NoSuchElementException:
                # Things are normal. Stop this test
                return
            except ValueError:
                # There's no data
                self.logger.info('No data for airport: %s', code.upper())
                with open(self.filename_stats, 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow([code.upper(), '0'])
                raise ValueError

        try:
            self.driver.get(self.url_prefix + code + self.url_postfix)

            try: test_have_data()
            except ValueError: return

            expand_upwards()
            expand_downwards()

            rows = prepare_rows()

            self.write_flight_rows(rows)
            self.write_stats_row(code, len(rows))
            
            # update total stats, wrap up
            self.stats['total_num_of_flights'] += len(rows)
            self.logger.info('Done scraping airport: %s. Got %s flights.', code.upper(), len(rows))

        except TimeoutException:
            self.airport_codes_list.append(code)
            self.logger.warning('Timeout scraping airport: %s. Will retry.', code.upper())
        except Exception as e:
            self.airport_codes_list.append(code)
            self.logger.exception(e)
            self.logger.exception('Error parsing airport: %s. Will retry.', code.upper())

if __name__ == "__main__":
    # Optional parameters of the scraper:
    # days_ago=0                   how many days ago (e.g. 1 day ago means get yesterday's data)
    # fetch_china=True             whether to get all china airports
    # additional_airports=[]       a list of additional airports to scrape
    airport_scrapper = AirportScraper(0, True, ['sin', 'hkg'])
    airport_scrapper.run()
