import csv
from datetime import datetime, date, timedelta
import time
import os
from pathlib import Path
import logging
import logging.config
from selenium import webdriver
#from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
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
    def __init__(self, 
                 days_ago=0, 
                 fetch_airport_list=False, 
                 countries=['china', 'south-korea', 'italy', 'united-kingdom', 'united-states'], 
                 additional_airports=[]):
        super().__init__()

        # constants
        self.url_prefix = 'https://www.flightradar24.com/data/airports/'
        self.url_postfix = '/departures'

        self.target_day = (date.today() - timedelta(days=days_ago)).strftime('%b %d')
        self.target_day_str = (date.today() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        self.prev_day = date.today() - timedelta(days=days_ago + 1)
        self.next_day = date.today() - timedelta(days=days_ago - 1)

        # paths
        self.output_dir = 'flightradar24_' + time.strftime('%Y-%m-%d_%H,%M,%S', time.localtime()) + '/'
        self.output_dir_path = (Path.cwd() / 'output' / self.output_dir).resolve()
        filename = self.target_day_str + '_flights.csv'
        self.filename_path = (self.output_dir_path / filename).resolve()
        logs_path = (self.output_dir_path / (filename[:-4] + '.log')).resolve()
        Path(self.output_dir_path).mkdir(parents=True, exist_ok=True)

        # important info
        self.fetch_airport_list = fetch_airport_list
        self.countries = countries
        self.airport_codes_list = additional_airports
        self.total_airports = 0
        self.stats = { 'total_num_of_flights': 0 }

        # driver
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(80)
        #ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        self.wait = WebDriverWait(self.driver, 15)

        # logger
        FORMAT = '%(asctime)-15s  %(message)s'
        logging.basicConfig(level=logging.INFO, format=FORMAT, filemode='a', filename=str(logs_path))
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialization finished.")

    def run(self):
        self.logger.info('Running parser for date: %s', self.target_day_str)
        self.logger.info('Files will be written in the directory: %s', self.output_dir_path)

        # scrape everything
        try:
            self.init_worklist()
            while self.airport_codes_list:
                self.scrape_airport(self.airport_codes_list[0])
                self.airport_codes_list.pop(0)

            self.logger.info('Total flights: %s for %s', self.stats['total_num_of_flights'], self.target_day_str)
        finally:
            self.logger.info('%s', self.airport_codes_list)
            self.driver.quit()

    def init_worklist(self):
        if self.fetch_airport_list:
            for country in self.countries:
                self.gen_airport_list(country)
        self.total_airports = len(self.airport_codes_list)

    def gen_airport_list(self, country):
        self.driver.get(self.url_prefix + country)
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
        with self.filename_path.open('a') as f:
            writer = csv.writer(f)
            writer.writerows([self.target_day_str] + row for row in rows if row)

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
                #airline = row.find_element_by_css_selector('td.cell-airline > a.notranslate.ng-binding').text.strip()
                #dest_city = row.find_element_by_css_selector('td:nth-child(3) > div:nth-child(1) > span').text.strip()
                dest_airport = row.find_element_by_css_selector('td:nth-child(3) > div:nth-child(1) > a.notranslate.ng-binding').text[1:-1]
                status = row.find_element_by_css_selector('td:nth-child(7) > span.ng-binding').text
                return [departure_airport, flight_time, flight_number, dest_airport, status]

            today_flights = self.driver.find_elements_by_css_selector("tr[data-date*='" + self.target_day + "']")
            return list(map(parse_flight_row, today_flights))

        def get_progress():
            now_scraped = self.total_airports - len(self.airport_codes_list) + 1
            return "({}/{} | {:.2f}%)".format(now_scraped, self.total_airports, now_scraped / self.total_airports * 100)

        def test_have_data():
            try:
                sorry = self.driver.find_element_by_xpath("//*[contains(text(), 'have any information about flights for this airport')]")
                if sorry and sorry.is_displayed(): raise ValueError
            except NoSuchElementException:
                # Things are normal. Stop this test
                return
            except ValueError:
                # There's no data
                self.logger.info('%s No data for airport: %s', get_progress(), code.upper())
                raise ValueError

        try:
            self.driver.get(self.url_prefix + code + self.url_postfix)

            try: test_have_data()
            except ValueError: return

            expand_upwards()
            expand_downwards()

            rows = prepare_rows()

            self.write_flight_rows(rows)
            
            # update total stats, wrap up
            self.stats['total_num_of_flights'] += len(rows)
            self.logger.info('%s Done scraping airport: %s. Got %s flights.', get_progress(), code.upper(), len(rows))

        except TimeoutException:
            self.airport_codes_list.append(code)
            self.logger.warning('Timeout scraping airport: %s. Will retry.', code.upper())
        except Exception as e:
            self.airport_codes_list.append(code)
            self.logger.exception(e)
            self.logger.exception('Error parsing airport: %s. Will retry.', code.upper())

if __name__ == "__main__":
    airports = [
        'SIN', 'HKG', 'JJN', 'AKU', 'AAT', 'AQG', 'AOG', 'AVA', 'YIE', 'AEB', 'NBS', 'BSD', 'BAV', 'RLK', 'BHY', 'PKX', 'NAY', 'PEK', 'BFJ', 'BPL', 
        'KJI', 'CWJ', 'CGQ', 'CGD', 'CSX', 'CIH', 'CZX', 'CHG', 'CDE', 'CTU', 'CIF', 'JUH', 'CKG', 'DLU', 'DLC', 'DDG', 'DCY', 'DQA', 'DAT', 'DYG', 
        'DAX', 'HXD', 'DSN', 'DOY', 'DNH', 'ENH', 'ERL', 'FUO', 'FUG', 'FYJ', 'FOC', 'KOW', 'GMQ', 'GYS', 'CAN', 'KWL', 'KWE', 'GYU', 'HAK', 'HLD', 
        'HMI', 'HDG', 'HGH', 'HZG', 'HRB', 'HFE', 'HEK', 'HNY', 'HET', 'HUO', 'HTN', 'HIA', 'HJJ', 'TXN', 'HYN', 'HUZ', 'JGS', 'JGD', 'JMU', 'JSJ', 
        'JGN', 'SWA', 'TNA', 'JIC', 'JDZ', 'JHG', 'JNG', 'JNZ', 'JIU', 'JXA', 'KJH', 'KGT', 'KRY', 'KHG', 'KRL', 'KMG', 'KCA', 'JMJ', 'LHW', 'LXA', 
        'LYG', 'LLB', 'LJG', 'LNJ', 'LFQ', 'LYI', 'HZH', 'LPF', 'LZH', 'LNL', 'LCX', 'LYA', 'LZO', 'LLV', 'LUM', 'NZH', 'MXZ', 'MIG', 'OHE', 'MDG', 
        'KHN', 'NAO', 'NKG', 'NNG', 'NTG', 'NNY', 'NGB', 'NLH', 'LZY', 'PZI', 'SYM', 'BPX', 'JIQ', 'TAO', 'IQN', 'SHP', 'BPE', 'BAR', 'NDG', 'JUZ', 
        'RIZ', 'SQJ', 'SYX', 'QSZ', 'PVG', 'SHA', 'SQD', 'DIG', 'WGN', 'HPG', 'SHE', 'SZX', 'RKZ', 'SHF', 'SJW', 'WDS', 'JZH', 'TCG', 'TYN', 'TVS', 
        'TCZ', 'TSN', 'THQ', 'TNH', 'TGO', 'TEN', 'TLQ', 'HLH', 'UCB', 'URC', 'WXN', 'WEF', 'WEH', 'WNH', 'WNZ', 'WUA', 'WUH', 'WSK', 'WUX', 'WUS', 
        'WUZ', 'XIY', 'GXH', 'XMN', 'XFN', 'XIC', 'XIL', 'ACX', 'XNN', 'XAI', 'NLT', 'WUT', 'XUZ', 'ENY', 'YNZ', 'YTY', 'YNJ', 'YNT', 'YBP', 'YIH', 
        'LDS', 'YIC', 'INC', 'YKH', 'YIN', 'YIW', 'LLF', 'YYA', 'UYN', 'YCU', 'YUS', 'NZL', 'ZQZ', 'YZY', 'ZHA', 'ZAT', 'CGO', 'ZHY', 'HSN', 'ZUH', 
        'WMT', 'ZYI', 'PUS', 'CJJ', 'TAE', 'KUV', 'KWJ', 'CJU', 'HIN', 'MWX', 'KPO', 'ICN', 'GMP', 'USN', 'WJU', 'YNY', 'RSU', 'ALL', 'AHO', 'AOI', 
        'AOT', 'BRI', 'BLQ', 'BZO', 'VBS', 'BDS', 'CAG', 'CTA', 'CIY', 'CRV', 'CUF', 'EBA', 'FLR', 'FOG', 'FRL', 'GOA', 'GRS', 'SUF', 'LMP', 'LCV', 
        'MXP', 'BGY', 'LIN', 'NAP', 'OLB', 'FNU', 'PMO', 'PNL', 'PMF', 'PEG', 'PSR', 'PSA', 'RAN', 'REG', 'RMI', 'FCO', 'CIA', 'QSR', 'SAY', 'TAR', 
        'TPS', 'TSF', 'TRS', 'TRN', 'VCE', 'VRN', 'ABZ', 'ACI', 'VLY', 'BRR', 'BWF', 'BFS', 'BHD', 'BEB', 'BHX', 'BBS', 'BLK', 'BOH', 'ESH', 'BRS',
        'BZZ', 'CBG', 'CAL', 'CWL', 'CAX', 'CEG', 'QUG', 'CVT', 'MME', 'DSA', 'DND', 'EMA', 'EOI', 'EDI', 'EXT', 'FIE', 'FAB', 'GLA', 'GLO', 'GCI', 
        'HYC', 'HUY', 'INV', 'ILY', 'IOM', 'ISC', 'JER', 'GBA', 'KOI', 'LEQ', 'QLA', 'LBA', 'LWK', 'LPL', 'LCY', 'LGW', 'LHR', 'BQH', 'LTN', 'STN', 
        'LDY', 'LYX', 'MAN', 'NCL', 'NQY', 'OBN', 'NRL', 'ORM', 'NWI', 'NQT', 'OXF', 'PPW', 'PSL', 'PIK', 'RCS', 'NDY', 'SCS', 'SOU', 'SEN', 'DGX',
        'SYY', 'SOY', 'LSI', 'SWS', 'TRE', 'WRT', 'WRY', 'WIC', 'ABR', 'ABI', 'VJI', 'ADT', 'ADK', 'AIK', 'AKI', 'CAK', 'AKC', 'AUK', 'ALM', 'ALS', 
        'ABY', 'ALB', 'ABQ', 'AEX', 'AXN', 'ABE', 'AIA', 'APN', 'ALN', 'AOO', 'TDW', 'AMA', 'AMW', 'AKP', 'ANC', 'MRI', 'AND', 'ANQ', 'ANI', 'QQK', 
        'ARB', 'ANP', 'ANB', 'ANV', 'AAF', 'APV', 'ATW', 'ADM', 'QQW', 'QQG', 'ATS', 'AVL', 'ASE', 'AST', 'ATO', 'MMI', 'AHN', 'QQR', 'FTY', 'PDK', 
        'ATL', 'ACY', 'BLM', 'ATK', 'MER', 'LEW', 'AUN', 'AUO', 'DNL', 'AGS', 'AUG', 'EDC', 'AUS', 'AVX', 'AVP', 'BKE', 'BFL', 'BWI', 'MTN', 'BGR', 
        'BHB', 'BRW', 'BTI', 'BVO', 'BOW', 'BVX', 'BTR', 'BTL', 'BAM', 'HSA', 'BIE', 'BFT', 'BPT', 'BFP', 'BKW', 'BED', 'BLV', 'BLI', 'BJI', 'BEH', 
        'XNA', 'BET', 'BTT', 'BVY', 'BIL', 'BGM', 'BHM', 'BIH', 'BIS', 'BCB', 'BID', 'BMG', 'BMI', 'TRI', 'BLH', 'BYH', 'BCT', 'BOI', 'BGD', 'BOS', 
        'WBU', 'BTF', 'BWG', 'BZN', 'BFD', 'BRD', 'BKG', 'PWT', 'KTS', 'BKX', 'BRO', 'BWD', 'BQK', 'SSI', 'BKC', 'BUF', 'IFP', 'QQF', 'BUR', 'BRL', 
        'QQY', 'QQU', 'BTV', 'MVW', 'BTP', 'BTM', 'CDW', 'CXL', 'CGE', 'QQC', 'CGI', 'MDH', 'CNM', 'CSN', 'QQV', 'CGZ', 'CPR', 'CDC', 'CID', 'CDR', 
        'CMI', 'JZI', 'CHS', 'CRW', 'CLT', 'CHO', 'CHA', 'CYF', 'CLS', 'QQP', 'VAK', 'CYS', 'ORD', 'UGN', 'QQI', 'MDW', 'DPA', 'PWK', 'RFD', 'AUZ', 
        'CIC', 'CNO', 'CVG', 'LUK', 'CKB', 'CKV', 'CEU', 'CGF', 'CLE', 'BKL', 'CVN', 'CTH', 'COD', 'COE', 'CBK', 'CDB', 'CGS', 'CLL', 'COS', 'MRC', 
        'CAE', 'CUB', 'COU', 'CLU', 'OSU', 'LCK', 'OLU', 'CMH', 'CSG', 'CPM', 'CCR', 'CON', 'USA', 'CXO', 'CDV', 'CRP', 'CEZ', 'CVO', 'CBF', 'CEC', 
        'CEW', 'CKN', 'CTY', 'CSV', 'DHT', 'DAL', 'ADS', 'DFW', 'RBD', 'DNN', 'DXR', 'DAN', 'DVN', 'GDV', 'DAY', 'MGY', 'DAB', 'SCC', 'DEC', 'DCU', 
        'DRT', 'QQD', 'DEN', 'QQH', 'BJC', 'APA', 'DSM', 'DSI', 'VPS', 'DET', 'DTW', 'YIP', 'DTL', 'DVL', 'DIK', 'DLG', 'DLN', 'DDC', 'DHN', 'DYL', 
        'PSK', 'DUJ', 'DBQ', 'DLH', 'DUC', 'DRO', 'DUA', 'EGE', 'EGV', 'HTO', 'ESN', 'ESD', 'EAU', 'EDE', 'EEK', 'ELD', 'EMT', 'ELP', 'ELI', 'ECG', 
        'EKX', 'EKI', 'EKO', 'ELN', 'ELM', 'ELY', 'EMK', 'WDG', 'ETS', 'QQE', 'ERI', 'ESC', 'EUG', 'ACV', 'EKA', 'EVV', 'EVM', 'PAE', 'FAI', 'FRM', 
        'FAR', 'FBL', 'FRG', 'FMN', 'FAY', 'FYV', 'FFM', 'FDY', 'FLG', 'FNT', 'FLO', 'FLD', 'FNL', 'FOD', 'FHU', 'FLL', 'FXE', 'FME', 'FMY', 'RSW', 
        'FPR', 'FSM', 'FWA', 'AFW', 'FTW', 'FYU', 'FFT', 'FKL', 'FDK', 'FET', 'FAT', 'FRD', 'FUL', 'GAD', 'GLE', 'GNV', 'GVL', 'GAI', 'GAL', 'GUP', 
        'GLS', 'GAM', 'GCK', 'GYY', 'GLR', 'GED', 'GGE', 'GCC', 'GGW', 'GFL', 'GTR', 'GLV', 'GLD', 'GSH', 'GCN', 'GFK', 'GRI', 'GJT', 'GRM', 'GRR', 
        'GPZ', 'GBD', 'GTF', 'GXY', 'GRB', 'GCY', 'GSO', 'GDC', 'GMU', 'PGV', 'GLH', 'GVT', 'GSP', 'GWO', 'GRD', 'GUF', 'GPT', 'GUC', 'GST', 'GUY', 
        'HGR', 'SUN', 'HNS', 'HAF', 'HAO', 'HNM', 'CMX', 'HRL', 'HAR', 'MDT', 'HRO', 'HFD', 'HSI', 'HBG', 'PIB', 'HVR', 'HHR', 'HDN', 'HYS', 'HYR', 
        'HWD', 'HLN', 'HIB', 'HKY', 'ITO', 'HHH', 'HOB', 'HWO', 'HCR', 'HOM', 'HNL', 'HNH', 'HPB', 'HQM', 'HOT', 'HUM', 'IWS', 'HOU', 'DWH', 'IAH', 
        'EFD', 'HNB', 'HTS', 'HTV', 'HSV', 'HON', 'HUT', 'HYA', 'IDA', 'ILI', 'IMM', 'IML', 'IPL', 'IDP', 'TYQ', 'QQQ', 'IND', 'INL', 'IYK', 'IOW', 
        'IMT', 'IWD', 'ISP', 'ITH', 'JAC', 'JAN', 'MJQ', 'HKS', 'MKL', 'JXN', 'JAX', 'CRG', 'VQQ', 'OAJ', 'JHW', 'JMS', 'JVL', 'JEF', 'JST', 'JOT', 
        'JBR', 'JLN', 'JNU', 'OGG', 'KOA', 'AZO', 'LUP', 'FCA', 'KLG', 'IKK', 'JCI', 'MCI', 'MKC', 'OJC', 'KUK', 'MKK', 'EAR', 'EEN', 'KLS', 'ENA', 
        'KNT', 'ENW', 'ERV', 'KTN', 'EYW', 'IAN', 'GRK', 'AKN', 'IGM', 'ISO', 'KPN', 'IRK', 'ISM', 'KVL', 'LMT', 'KLW', 'TYS', 'OBU', 'ADQ', 'KNK', 
        'KKH', 'KOT', 'OTZ', 'KKA', 'UUK', 'KWT', 'KWK', 'LSE', 'LGD', 'POC', 'LCI', 'LAF', 'LFT', 'LGC', 'JHM', 'LCH', 'CWF', 'LCQ', 'HII', 'LJN', 
        'AIZ', 'LAL', 'LAA', 'LNY', 'WJF', 'LNS', 'LAN', 'LAR', 'LRD', 'LRU', 'LAS', 'VGT', 'HSH', 'LVS', 'LBE', 'LUL', 'LWC', 'LWM', 'LZU', 'LAW', 
        'LEB', 'QQL', 'LEE', 'LWB', 'LWS', 'LWT', 'LEX', 'LBL', 'LIH', 'AOH', 'LIC', 'LNK', 'LDJ', 'LIT', 'LVK', 'LGU', 'LOZ', 'LGB', 'GGG', 'LAX', 
        'WHP', 'LFN', 'SDF', 'LOU', 'LBB', 'LDM', 'LFK', 'LBT', 'LYH', 'MCD', 'MCN', 'MAE', 'MSN', 'DXE', 'MMH', 'MNZ', 'MHT', 'MHK', 'MBL', 'MTW', 
        'MKT', 'MFD', 'MEO', 'MZJ', 'MTH', 'MRK', 'MRF', 'OAR', 'MWA', 'MQT', 'ASL', 'MML', 'MVY', 'MRB', 'MYV', 'MCW', 'MSS', 'MLC', 'MFE', 'MYL', 
        'MCK', 'MCG', 'QQT', 'MMV', 'MFR', 'MLB', 'MEM', 'QQM', 'MCE', 'MEI', 'COI', 'MSC', 'OPF', 'MIA', 'MIO', 'TMB', 'MWO', 'MAF', 'MDD', 'MLS', 
        'NQA', 'MIV', 'MKE', 'MWC', 'MEV', 'QQJ', 'MWL', 'MSP', 'FCM', 'QQA', 'MIC', 'ARV', 'MOT', 'MSO', 'MHE', 'CNY', 'MBY', 'BFM', 'MOB', 'MOD', 
        'MHV', 'MLI', 'MLU', 'MTP', 'MRY', 'MVE', 'MGM', 'MSV', 'MTJ', 'MRN', 'MGW', 'MMU', 'MOR', 'MVL', 'MWH', 'MGR', 'LLY', 'MPO', 'WMH', 'NUQ', 
        'MOU', 'MIE', 'MUT', 'MSL', 'MKG', 'MYR', 'ACK', 'APC', 'APF', 'ASH', 'BNA', 'HEZ', 'EWB', 'EWN', 'QQZ', 'HVN', 'ARA', 'GON', 'MSY', 'NEW', 
        'QQB', 'EWR', 'SWF', 'JFK', 'JRB', 'LGA', 'NPT', 'ONP', 'PHF', 'WWT', 'TNU', 'EWK', 'IAG', 'WTK', 'OLS', 'OME', 'OFK', 'ORF', 'OUN', 'OTH', 
        'CRE', 'LBF', 'IKB', 'OWD', 'NOT', 'NUI', 'OAK', 'PTK', 'OCF', 'OCE', 'OGD', 'OGS', 'OBE', 'OKC', 'PWA', 'OLV', 'OLM', 'OMA', 'MIQ', 'OMK',
        'ONO', 'ONT', 'SNA', 'OGB', 'SFB', 'ORL', 'MCO', 'OSC', 'OSH', 'OTM', 'OWB', 'UOX', 'OXC', 'OXR', 'PAH', 'PGA', 'PSN', 'UDD', 'PSP', 'PMD', 
        'PAO', 'ECP', 'PKD', 'PKB', 'PSC', 'PRB', 'SFZ', 'PEQ', 'PLN', 'PDT', 'PNS', 'PIA', 'VYS', 'PSG', 'PHL', 'BBX', 'PNE', 'DVT', 'GYR', 'PHX', 
        'AZA', 'LQK', 'PIR', 'PTS', 'AGC', 'PIT', 'PSF', 'PTU', 'PBG', 'PYM', 'PIH', 'PHO', 'PIZ', 'PMP', 'PPM', 'PNC', 'POF', 'CLM', 'PHN', 'PTV', 
        'HIO', 'PWM', 'PDX', 'TTD', 'PSM', 'PTW', 'POU', 'PTT', 'PRC', 'PQI', 'PUC', 'PVD', 'PVC', 'PVU', 'PUB', 'PUW', 'PGD', 'UIN', 'KWN', 'RAC', 
        'RDU', 'RAP', 'RWL', 'RDG', 'RBL', 'RDB', 'RDD', 'RDM', 'RNO', 'RNT', 'RHI', 'RIE', 'RLD', 'RID', 'RIC', 'RIL', 'RAL', 'RIV', 'RIW', 'ROA', 
        'ROC', 'RST', 'RKH', 'RKS', 'RKD', 'RKP', 'RWI', 'ROG', 'RME', 'RMG', 'LOT', 'RBG', 'ROW', 'RUI', 'RSH', 'RSN', 'RUT', 'SAC', 'MCC', 'MHR', 
        'SMF', 'SAD', 'MBS', 'STG', 'STJ', 'SLE', 'SLO', 'SLT', 'SLN', 'SNS', 'SBY', 'SRW', 'SLC', 'SJT', 'SAT', 'SSF', 'SBD', 'SQL', 'MYF', 'SAN', 
        'SEE', 'CLD', 'SDM', 'SFO', 'RHV', 'SJC', 'SBP', 'HYI', 'SDP', 'SFM', 'SBA', 'SAF', 'SMX', 'SMO', 'SZP', 'STS', 'SQA', 'SLK', 'SRQ', 'CIU', 
        'SAV', 'SVA', 'SCM', 'SCH', 'BFF', 'SCF', 'SRC', 'SEA', 'BFI', 'SEF', 'SDX', 'WLK', 'SEG', 'GKT', 'SKK', 'SBM', 'SHR', 'PNX', 'SHH', 'SOW', 
        'SHV', 'DTN', 'SHG', 'QQS', 'SDY', 'SNY', 'SVC', 'SUX', 'FSD', 'SIT', 'SGY', 'MQY', 'SBN', 'TVL', 'SOP', 'SPA', 'SPF', 'SPW', 'SFF', 'GEG', 
        'SPZ', 'SGF', 'CEF', 'SGH', 'SPI', 'UST', 'STC', 'SGU', 'SUS', 'CPS', 'STL', 'KSM', 'SMK', 'STP', 'SNP', 'PIE', 'SPG', 'SCE', 'TBR', 'SVH', 
        'SHD', 'SBS', 'SQI', 'STE', 'SWO', 'SCK', 'BDR', 'SUA', 'SUE', 'SGR', 'SUM', 'SUW', 'SVE', 'SYR', 'TIW', 'ASN', 'TLH', 'CLW', 'TPF', 'VDF', 
        'TPA', 'TAL', 'TSM', 'TEX', 'TPL', 'HUF', 'TEB', 'TXK', 'DLS', 'TRM', 'TVF', 'TVI', 'TMA', 'OTK', 'TIX', 'TOC', 'TOG', 'OOK', 'TDZ', 'TOL', 
        'MJX', 'XSD', 'FOE', 'TOP', 'TOA', 'TVC', 'TTN', 'TOI', 'TKF', 'TCS', 'TUS', 'AVW', 'THA', 'TUL', 'RVS', 'UTM', 'TUP', 'TCL', 'TWF', 'TYR', 
        'UKI', 'UNK', 'DUT', 'CCB', 'UVA', 'VCB', 'VDZ', 'VLD', 'VTN', 'VPZ', 'VNY', 'VNC', 'VEL', 'VRB', 'VCT', 'VCV', 'VIS', 'ACT', 'CNW', 'MUE', 
        'AIN', 'WAA', 'ALW', 'RBW', 'DCA', 'IAD', 'WSG', 'ALO', 'ART', 'ATY', 'WVL', 'WVI', 'UES', 'CWA', 'AUW', 'AYS', 'TBN', 'EAT', 'ENV', 'ETB', 
        'AWM', 'PBI', 'LNA', 'WYS', 'WST', 'BAF', 'FOK', 'HLG', 'WMO', 'HPN', 'BEC', 'ICT', 'KIP', 'SPS', 'WWD', 'IPT', 'XWA', 'LNN', 'WLW', 'ILG', 
        'ILM', 'ILN', 'WGO', 'WDR', 'BDL', 'WMC', 'INW', 'INT', 'GIF', 'ISS', 'OLF', 'WWR', 'BJJ', 'ORH', 'WRG', 'YKM', 'YAK', 'THV', 'YNG', 'YUM', 
        'ZZV', 'ZPH'
    ]
    # Optional parameters of the scraper:
    # days_ago=0                   how many days ago (e.g. 1 day ago means get yesterday's data)
    # additional_airports=[]       a list of additional airports to scrape
    current_time = datetime.now()
    today_deadline = current_time.replace(hour=21, minute=0, second=0, microsecond=0)
    if current_time > today_deadline:
        days_ago = 0
    else:
        days_ago = 1
    airport_scrapper = AirportScraper(days_ago, countries=['china', 'south-korea', 'italy', 'united-kingdom', 'united-states'], additional_airports=airports)
    airport_scrapper.run()
