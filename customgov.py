import csv
from datetime import datetime, date, timedelta
import time
import os
from pathlib import Path
from customgov_links import links as link_list
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


class CustomScraper(object):
    def __init__(self):
        super().__init__()
        print('Initializing...')

        # constants
        self.index_url = 'http://english.customs.gov.cn/statics/report/monthly.html#'
        self.output_dir = time.strftime('%Y-%m-%d_%H,%M,%S', time.localtime()) + '/'

        # important info
        self.link_list = []

        # driver
        options = Options()
        # options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.set_page_load_timeout(1000)
        self.driver.implicitly_wait(10)

    def run(self):
        # make dir
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        print('Files will be written in the directory:', self.output_dir)

        try:
            #self.gen_link_list()
            self.link_list = link_list
            for link in self.link_list:
                self.scrape_link(link)
        finally:
            self.driver.quit()

    def gen_link_list(self):
        self.driver.get(self.index_url)
        table_rows = (self.driver
                .find_element_by_css_selector('div.nr-n-content-detail > table > tbody')
                .find_elements_by_css_selector('tr:nth-child(14), tr:nth-child(15')
            )
        a_list = list(map(lambda x: x.find_elements_by_css_selector('td:nth-child(2) > a'),
                          table_rows))
        a_list = (lambda l: [item for sublist in l for item in sublist])(a_list)
        self.link_list = list(map(lambda a: a.get_attribute('href'), a_list))
        print(self.link_list)

    def scrape_link(self, link):
        def get_row_with_title(title):
            b = self.driver.find_element_by_xpath("//*[contains(text(), '" + title + "')]")
            tr = b.find_element_by_xpath("../../..")
            return tr

        def parse_row(tr):
            tds = tr.find_elements_by_tag_name('td')
            data_list = list(map(lambda td: td.text.strip().replace(',', ''), tds))
            return data_list

        try:
            self.driver.get(link)

            # get important rows
            important_titles = [
                'Coke and semi-coke',
                'Crude petroleum oil',
                'Gasoline',
                'Kerosene',
                'Diesel oil',
                'Other fuel oil',
                'Naphtha',
                'Liguified natural gases',
                'Natural gases in gaseous state'
            ]

            trs = list(map(get_row_with_title, important_titles))
            data = list(map(parse_row, trs))

            # write csv
            filename = (self.driver.title
                    .strip()
                    .replace('(13) Major ', '')
                    .replace('Commodities in Quantity and Value,', '')
                    .replace('.', ' ')
                    .split())
            filename = '-'.join(reversed(filename)) + '.csv'
            csv_headers = ['commodity', 'unit', 'q1', 'v1', 'q2', 'v2', 'q3', 'v3']
            with open(self.output_dir + filename, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(csv_headers)
                writer.writerows(data)

            print('Done parsing:', filename)

        except Exception as e:
            print(e)


if __name__ == "__main__":
    # Optional parameters of the scraper:
    # days_ago=0                   how many days ago (e.g. 1 day ago means get yesterday's data)
    # fetch_china=True             whether to get all china airports
    # additional_airports=[]       a list of additional airports to scrape
    custom_scraper = CustomScraper()
    custom_scraper.run()
