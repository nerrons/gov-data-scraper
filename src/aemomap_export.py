from datetime import datetime, date, timedelta
import logging
import os
from pathlib import Path
import time
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

class AemoMapScraper(object):
    def __init__(self):
        super().__init__()

        # constants
        self.today = date.today().strftime('%d/%m/%Y')
        self.url_index = 'https://www.aemo.com.au/energy-systems/gas/gas-bulletin-board-gbb/interactive-map-gbb'
        self.output_dir = type(self).__name__ + '_' + time.strftime('%Y-%m-%d_%H,%M,%S', time.localtime()) + '/'

        self.tables = ['summary', 'pipelines', 'production', 'storage']
        self.filenames = {
            table: '{}{}_{}.csv'.format(self.output_dir, date.today().strftime('%Y-%m-%d'), table)
                for table in self.tables
        }

        # driver
        options = Options()
        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.download.dir", str(Path.cwd()) + '/' + self.output_dir)
        fp.set_preference("browser.helperApps.neverAsk.openFile", "text/csv")
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
        fp.set_preference("pdfjs.disabled", True)
        self.driver = webdriver.Firefox(fp, options=options)
        # ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        self.wait = WebDriverWait(self.driver, 20)
        self.driver.implicitly_wait(30)
        self.actions = ActionChains(self.driver)

        # logger
        LOGGER_FORMAT = '%(asctime)-15s  %(message)s'
        logging.basicConfig(level=logging.INFO, format=LOGGER_FORMAT)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialization finished.")

    def run(self):
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.logger.info('Files will be written in the directory: %s', self.output_dir)

        try:
            self.setup()

            for table in self.tables:
                self.scrape_table(table)

            self.logger.info('All done.')
        except:
            self.logger.exception('bad')
        finally:
            self.driver.quit()

    def setup(self):
        self.driver.get(self.url_index)
        confirm_a = self.driver.find_element_by_xpath("//a[contains(text(), 'Confirm')]")
        confirm_a.click()

        iframe = self.driver.find_element_by_css_selector('div.iframe iframe')
        self.driver.switch_to.frame(iframe)
        try:
            agree_b = self.driver.find_element_by_css_selector(
                "button.wc-button.modal-button.primary")
            agree_b.click()
        except:
            self.logger.exception('Error getting agree_b.')

    def scrape_table(self, table):
        # refresh, get into iframe
        self.driver.get(self.url_index)
        iframe = self.driver.find_element_by_css_selector('div.iframe iframe')
        self.driver.switch_to.frame(iframe)

        # switch to required table
        table_b_str = '#map-{}-button'.format(table)
        table_b = self.driver.find_element_by_css_selector(table_b_str)
        table_b.click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".active" + table_b_str)))

        # click two export buttons
        export_b = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.date-control > button.map-button.export')))
        export_b.click()
        export_submit_b = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.modal-footer button.map-button.export')))
        export_submit_b.click()

        # wait for the download to complete
        while(True):
            files = ' '.join([str(x).lower() for x in Path('./' + self.output_dir).iterdir()])
            self.logger.info('%s', files)
            if table in files: return
            time.sleep(1)


if __name__ == "__main__":
    s = AemoMapScraper()
    s.run()
