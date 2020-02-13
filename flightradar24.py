import csv
from datetime import datetime, date, timedelta
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


class AirportScraper(object):
    def __init__(self, days_ago=0, fetch_china=True, additional_airports=[]):
        super().__init__()
        print('Initializing...')

        # constants
        self.url_prefix = 'https://www.flightradar24.com/data/airports/'
        self.url_postfix = '/departures'

        self.today_str = (date.today() - timedelta(days=days_ago)).strftime('%b %d')
        self.prev_day = date.today() - timedelta(days=days_ago+1)
        self.next_day = date.today() - timedelta(days=days_ago-1)

        filename_stem = time.strftime('%Y-%m-%d_%H,%M,%S', time.localtime()) + '_'
        self.filename_flights = filename_stem + 'flights.csv'
        self.filename_stats = filename_stem + 'stats.csv'

        # important info
        self.fetch_china = fetch_china
        self.airport_codes_list = additional_airports
        self.stats = { 'total_num_of_flights': 0 }

        # driver
        options = Options()
        # options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(10)

    def run(self):
        print('Scraping flights of date: ' + self.today_str)
        print('Files to be written: ' + self.filename_flights + ', ' + self.filename_stats)

        # write csv headers
        with open(self.filename_flights, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(['departure_airport', 'time', 'flight_number', 'dest_airport', 'status'])
        with open(self.filename_stats, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(['departure_airport', 'num_of_flights'])

        try:
            if self.fetch_china: self.gen_airport_list()
            for code in self.airport_codes_list:
                self.scrape_airport(code)
            print('Total flights: ', self.stats['total_num_of_flights'])
        finally:
            self.driver.quit()

    def gen_airport_list(self):
        self.driver.get(self.url_prefix + 'china')
        table_rows = (self.driver
                .find_element_by_css_selector('#tbl-datatable > tbody')
                .find_elements_by_css_selector('tr:not(.header)')[1:]
            )
        self.airport_codes_list = list(map(
                lambda x: (x
                        .find_element_by_css_selector('td:nth-child(2) > a')
                        .get_attribute('href')
                        .rpartition('/')[2]
                    ),
                table_rows))
        print('Airport list: ', list(map(lambda x: x.upper(), self.airport_codes_list)))

    def scrape_airport(self, code):
        def parse_separator_date(text):
            return datetime.strptime('2020 ' + text, '%Y %A, %b %d').date()
        
        def expand(button_text, row_index, standard):
            date_rows = self.driver.find_elements_by_class_name('row-date-separator')
            button = self.driver.find_element_by_xpath("//*[contains(text(), '" + button_text + "')]")
            stuck_counter = 100
            while (stuck_counter > 0
                    and button.is_displayed()
                    and standard(parse_separator_date(date_rows[row_index].text))):
                try:
                    button.click()
                    last_len = len(date_rows)
                    date_rows = self.driver.find_elements_by_class_name('row-date-separator')
                    if len(date_rows) == last_len: stuck_counter -= 1
                except StaleElementReferenceException:
                    continue
        
        def expand_upwards():
            expand('Load earlier flights', 0, lambda x: self.prev_day <= x)
        def expand_downwards():
            expand('Load later flights', -1, lambda x: x <= self.next_day)

        # get all today's flights and extract info
        def prepare_rows():
            # parse a tr and get details
            def parse_flight_row(row):
                departure_airport = code.upper()
                flight_time = row.find_element_by_css_selector('td.ng-binding').text
                flight_number = row.find_element_by_css_selector('td.cell-flight-number > a.notranslate.ng-binding').text
                dest_airport = row.find_element_by_css_selector('td:nth-child(3) > div:nth-child(1) > a.notranslate.ng-binding').text[1:-1]
                status = row.find_element_by_css_selector('td:nth-child(7) > span.ng-binding').text
                return (departure_airport, flight_time, flight_number, dest_airport, status)

            today_flights = self.driver.find_elements_by_css_selector("tr[data-date*='" + self.today_str + "']")
            return list(map(parse_flight_row, today_flights))

        def test_have_data():
            try:
                self.driver.find_element_by_class_name('row-date-separator')
            except:
                with open(self.filename_stats, 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow([code.upper(), '0'])
                raise Exception

        try:
            self.driver.get(self.url_prefix + code + self.url_postfix)

            try: test_have_data()
            except: return

            expand_upwards()
            expand_downwards()

            rows = prepare_rows()

            # write flight details
            with open(self.filename_flights, 'a') as f:
                writer = csv.writer(f)
                writer.writerows(row for row in rows if row)

            # write flight stats
            with open(self.filename_stats, 'a') as f:
                writer = csv.writer(f)
                writer.writerow([code.upper(), len(rows)])
            
            # update total stats, wrap up
            self.stats['total_num_of_flights'] += len(rows)
            print('Done scraping airport:', code.upper() + '. Got', len(rows), 'flights.')

        except Exception as e:
            print(e)


if __name__ == "__main__":
    # Optional parameters of the scraper:
    # days_ago=0                   how many days ago (e.g. 1 day ago means get yesterday's data)
    # fetch_china=True             whether to get all china airports
    # additional_airports=[]       a list of additional airports to scrape
    airport_scrapper = AirportScraper(1, False, ['sin', 'hkg'])
    airport_scrapper.run()
