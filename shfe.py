from datetime import datetime, date, timedelta
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options

url = 'http://www.shfe.com.cn/statements/dataview.html?paramid=delaymarket_fu'

options = Options()
driver = webdriver.Firefox(options=options)
driver.implicitly_wait(20)
driver.set_page_load_timeout(120)
driver.get(url)

# change these
year = '2017'
month = '六月'
day = '15'


fu_button = driver.find_element_by_id('delaymarket_fu')
fu_button.click()

select_year = Select(driver.find_element_by_css_selector('select.ui-datepicker-year'))
select_year.select_by_visible_text(year)
select_month = Select(driver.find_element_by_css_selector('select.ui-datepicker-month'))
select_month.select_by_visible_text(month)

calendar_tbody = driver.find_element_by_css_selector('table.ui-datepicker-calendar > tbody')
day_a = calendar_tbody.find_element_by_xpath("//a[@class='ui-state-default' and contains(text(), '" + day + "')]")
day_a.click()