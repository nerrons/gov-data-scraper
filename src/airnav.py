from Scraper import Scraper

class AirnavScraper(Scraper):
    def __init__(self, airports):
        super().__init__(['airport', 'lat', 'long'])
        self.url_stem = r'http://airnav.com/airport/'
        self.airports = airports

    def run(self):
        def proc():
            for airport in self.airports:
                self.scrape_airnav(airport)
        df = super().scrape(proc)
        df.to_csv(self.file_path)
        return df

    def scrape_airnav(self, airport):
        css, allcss, xpath, allxpath = self.shorter_find() # pylint: disable=unused-variable
        
        self.driver.get(self.url_stem + airport)

        the_td = xpath('/html/body/table[5]/tbody/tr/td[1]/table[1]/tbody/tr[2]/td[2]').text
        splitted = the_td.split('\n')
        pure_number_lat_long = [ll for ll in splitted if ('N' not in ll) and ('W' not in ll) and ('estimate' not in ll)][0]
        row = [airport] + pure_number_lat_long.split(',')

        self.write_rows([row], True)

if __name__ == "__main__":
    airports = ['w17']
    s = AirnavScraper(airports)
    print(s.run())

    