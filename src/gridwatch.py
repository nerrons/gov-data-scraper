import time
import pandas as pd
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, 
    StaleElementReferenceException, 
    ElementNotInteractableException,
    TimeoutException
)


# setup
options = Options()
#options.headless = True
fp = webdriver.FirefoxProfile()
fp.set_preference("browser.download.folderList", 2)
fp.set_preference("browser.download.dir", str(Path.cwd()))
fp.set_preference("browser.helperApps.neverAsk.openFile", "text/csv")
fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
driver = webdriver.Firefox(fp, options=options)
driver.set_window_size(1920, 1080) # needed to assure button is in viewport
wait = WebDriverWait(driver, 20)
driver.implicitly_wait(30)
actions = ActionChains(driver)

# find elem and click
driver.get('http://gridwatch.templar.co.uk/download.php')
plus_b = driver.find_element_by_css_selector('#startyearvalue + div')
year = int(driver.find_element_by_css_selector('#startyearvalue').text)
while year < 2019:
    plus_b.click()
    year = int(driver.find_element_by_css_selector('#startyearvalue').text)

download_b = driver.find_element_by_xpath("//div[contains(text(), 'DOWNLOAD')]")
download_b.click()

while(True):
    files = ' '.join([str(x).lower() for x in Path.cwd().iterdir()])
    if '.part' not in files: break
    time.sleep(1)

# wrap up
print(f'csv downloaded to {Path.cwd()}')
