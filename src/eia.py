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
options.headless = True
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
driver.get('https://www.eia.gov/opendata/qb.php?category=3389935&sdid=EBA.US48-ALL.D.H')
rect = driver.find_element_by_css_selector('.highcharts-container svg .highcharts-button > rect')
actions.move_to_element(rect).click(rect).perform()
context_menu = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.contextmenu')))
download_b = context_menu.find_element_by_xpath("//div[contains(text(), 'Download Data')]")
download_b.click()

# wrap up
print(f'csv downloaded to {Path.cwd()}')
driver.quit()