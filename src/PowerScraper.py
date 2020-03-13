from Scraper import Scraper

class PowerScraper(Scraper):
    def __init__(self):
        super().__init__(['update_time', 'facility', 'status'])

        # constants override
        self.urls = {
            'genkai' :'http://www.kyuden.co.jp/php/nuclear/genkai/g_power.php',
            'sendai': 'http://www.kyuden.co.jp/php/nuclear/sendai/s_power.php'
        }
        self.DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def run(self):
        def proc():
            self.scrape_kyuden('genkai')
            self.scrape_kyuden('sendai')
        return super().scrape(proc)

    def scrape_kyuden(self, facility):
        css, allcss, xpath, allxpath = self.shorter_find() # pylint: disable=unused-variable

        def parse_tr(prefix_cols):
            def f(tr):
                try:
                    data = css('td', tr).text.strip()
                    unit = self.full2half(css('th', tr).text[0])
                    return prefix_cols + ['{} #{}'.format(facility, unit), data]
                except ValueError:
                    return []
            return f

        self.driver.get(self.urls[facility])
        last_update_str = self.xpath('//*[@id="lastupdate" and contains(text(), "月")]').text
        last_update = self.standardize_date('%Y年%m月%d日 %H時%M分')(last_update_str)
        tbody_tups = [ ([last_update], tbody)
                for tbody in allcss('div.nuclear__dataArea > table.newclear__hatsudenki > tbody') ]
        trs_tups = [ (ttup[0], allcss('tr', ttup[1])) for ttup in tbody_tups ]
        rows = sum([ [ parse_tr(ttup[0])(tr) for tr in ttup[1] ] for ttup in trs_tups], [])
        self.write_rows(rows)

if __name__ == "__main__":
    s = PowerScraper()
    print(s.run())
