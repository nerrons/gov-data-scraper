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

class Downloader(object):
    def __init__(self):
        # constants
        self.url_index = ''

        # config
        options = Options()
        options.headless = True
        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.download.dir", str(Path.cwd()))
        fp.set_preference("browser.helperApps.neverAsk.openFile", "text/csv")
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")

        # export driver objects
        self.driver = webdriver.Firefox(fp, options=options)
        self.driver.set_window_size(1920, 1080) # needed to assure button is in viewport
        self.wait = WebDriverWait(self.driver, 20)
        self.driver.implicitly_wait(30)
        self.actions = ActionChains(self.driver)

