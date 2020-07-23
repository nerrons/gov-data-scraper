import time
from Scraper import Scraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class ChangiScraper(Scraper):
    def __init__(self):
        super().__init__(['status', 'time', 'flight_code', 'airline', 'city'])
        self.urls = {
            'arr': r'https://www.changiairport.com/content/cag/en/flights/arrivals.html#?status=arrival&date=today&terminal=all&time=all',
            'dep': r'https://www.changiairport.com/content/cag/en/flights/departures.html#?status=departure&date=today&terminal=all&time=all'
        }

    def run(self):
        def proc():
            self.scrape_changi('arr')
            self.scrape_changi('dep')
        return super().scrape(proc)

    def scrape_changi(self, page):
        css, allcss, xpath, allxpath = self.shorter_find() # pylint: disable=unused-variable

        # If status is not present in the original webpage, it will be represented by "--TBD--"
        def parse_content(div):
            try:
                detail = css('.row.flight-detail', div)
                status = css('.flight-status > span', detail).text.strip()
                if not status: status = '--TBD--'
                flight_time = css('.col-time > span.color-custom-1', detail).text
                flight_code = css('.flight-code > .flight-info > span.code', detail).text
                airline = css('.flight-code > .flight-info > span.desc', detail).text
                city = css('.flight-name', detail).text
                return [status, flight_time, flight_code, airline, city]
            except ValueError:
                return []
        
        self.driver.get(self.urls[page])
        # wait until loading is complete
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.flight-container__load-warp')))

        data_rows = [ parse_content(c) for c in allcss('.flight-result__row') ]
        self.write_rows(data_rows, True)

if __name__ == "__main__":
    s = ChangiScraper()
    print(s.run())

    