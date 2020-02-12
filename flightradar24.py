import csv
from datetime import date
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

class AirportScraper(object):
    def __init__(self):
        super().__init__()
        print('Initializing...')

        self.url_prefix = 'https://www.flightradar24.com/data/airports/'
        self.url_postfix = '/departures'
        self.today = date.today().strftime('%b %d')
        self.filename_stem = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime()) + '_'
        self.filename_flights = self.filename_stem + 'flights.csv'
        self.filename_stats = self.filename_stem + 'stats.csv'
        self.airport_codes_list = []

        self.stats = { 'total_num_of_flights': 0 }

        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(10)

    def run(self):
        print('Files to be written: ' + self.filename_flights + ', ' + self.filename_stats)
        with open(self.filename_flights, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(['departure_airport', 'time', 'flight_number', 'dest_airport'])
        with open(self.filename_stats, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(['departure_airport', 'num_of_flights'])
        
        try:
            self.gen_airport_list()
            for code in self.airport_codes_list:
                self.scrape_airport(code)
            print('Total flights departed from china: ', self.stats['total_num_of_flights'])
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
        try:
            self.driver.get(self.url_prefix + code + self.url_postfix)
            try:
                top_date = self.driver.find_element_by_class_name('row-date-separator')
            except NoSuchElementException:
                return

            # expand upwards
            today_date_text = top_date.text
            earlier_button = self.driver.find_element_by_xpath("//*[contains(text(), 'Load earlier flights')]")
            while earlier_button.is_displayed() and self.today in top_date.text:
                earlier_button.click()
                # time.sleep(1)
                top_date = self.driver.find_element_by_class_name('row-date-separator')
            
            # expand downwards
            later_button = self.driver.find_element_by_xpath("//*[contains(text(), 'Load later flights')]")
            date_rows = self.driver.find_elements_by_class_name('row-date-separator')
            while later_button.is_displayed() and len(date_rows) < 3:
                later_button.click()
                # time.sleep(1)
                date_rows = self.driver.find_elements_by_class_name('row-date-separator')

            # parse a tr and get details
            def parse_flight_row(row):
                departure_airport = code.upper()
                flight_time = row.find_element_by_css_selector('td.ng-binding').text
                flight_number = (row
                        .find_element_by_css_selector('td.cell-flight-number > a.notranslate.ng-binding')
                        .text
                    )
                dest_airport = (row
                        .find_element_by_css_selector('td:nth-child(3) > div:nth-child(1) > a.notranslate.ng-binding')
                        .text[1:-1]
                    )
                # You can use this if you want to
                # status = (row
                #         .find_element_by_css_selector('td:nth-child(7) > span.ng-binding')
                #         .text
                #     )
                return (departure_airport, flight_time, flight_number, dest_airport)

            # get all today's flights and extract info
            today_flights = self.driver.find_elements_by_xpath("//tr[@data-date='" + today_date_text + "']")
            rows = list(map(parse_flight_row, today_flights))

            # write flight details
            with open(self.filename_flights, 'a') as f:
                writer = csv.writer(f)
                writer.writerows(row for row in rows if row)

            # write flight stats
            with open(self.filename_stats, 'a') as f:
                writer = csv.writer(f)
                writer.writerow([code.upper(), len(rows)])
            
            # update total stats
            self.stats['total_num_of_flights'] += len(rows)

        finally:
            print('Done scraping airport: ' + code.upper() + '.')

if __name__ == "__main__":
    airport_scrapper = AirportScraper()
    airport_scrapper.run()
