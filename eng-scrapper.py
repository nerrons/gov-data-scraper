import argparse
import csv
import time
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

# setup
parser = argparse.ArgumentParser(description='Turn gov data to csv.')
parser.add_argument(
    'timeframe', 
    nargs='?', 
    default='201911', 
    help='Default to 201911'
)
parser.add_argument(
    'url', 
    nargs='?', 
    default='http://data.stats.gov.cn/english/easyquery.htm?cn=E0101', 
    help='Default to the page of 月度能源产品产量'
)
args = vars(parser.parse_args())
print('Initializing...')
url = args['url']
timeframe = args['timeframe']
filename = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime()) + '.csv'
options = Options()
# options.headless = True
browser = webdriver.Firefox(options=options)
# browser.implicitly_wait(100)
wait = WebDriverWait(browser, 20)

# repeated patterns
def wait_for_loading():
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'loadingBox')))

def click_on_text(text):
    wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, text)))
    browser.find_element_by_partial_link_text(text).click()

try:
    print('Fetching page. Be patient...')
    browser.get(url)

    # Click on left panel
    click_on_text('Energy')
    click_on_text('Output of Energy Products')
    click_on_text('Crude oil')

    # Gather from the right table
    wait_for_loading()
    print('wasted')
    

    # # select timeframe
    # print('Mimicking clicks...')
    # dtHead = browser.find_element_by_css_selector('#mySelect_sj .dtHead')
    # dtHead.click()
    # dt11 = browser.find_element_by_css_selector('#mySelect_sj .dtList li[code="' + timeframe + '"]')
    # dt11.click()

    # # TODO: use expected_conditions for waiting
    # print('Waiting for loading...')
    # time.sleep(5)

    # # find main table
    # print('Scraping data...')
    # soup = BeautifulSoup(browser.page_source, features='html.parser')
    # table = soup.find('table', attrs={ 'id': 'tabledata' })

    # # get headers
    # headers = [ header.text.strip() for header in table.find_all('th') ]

    # # get rows
    # rows = []
    # for row in table.find_all('tr'):
    #     rows.append([ val.text.strip() for val in row.find_all('td') ])

    # # write csv
    # print('Writing csv...')
    # with open(filename, 'w') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(headers)
    #     writer.writerows(row for row in rows if row)

finally:
    # browser.quit()
    print('All done. File written to ' + filename)
