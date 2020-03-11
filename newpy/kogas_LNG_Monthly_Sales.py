
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
#from glencorepy.data import sql
import datetime as dt
import re
import numpy as np
import googletrans
from googletrans import Translator
from datetime import date, datetime, timedelta

#Update check point.


def Clean_names(Rename): 
    # Search for opening bracket in the name followed by 
    # any characters repeated any number of times 
    if re.search('\n.*', Rename): 
  
        # Extract the position of beginning of pattern 
        pos = re.search('\n.*', Rename).start() 
  
        # return the cleaned name 
        return Rename[:pos]
  
    else: 
        # if clean up needed return the same name 
        return Rename




options = Options()

prefs = {
  "translate_whitelists": {"ko":"en"},
  "translate":{"enabled":"true"}
}
options.add_experimental_option("prefs", prefs)


browser = webdriver.Chrome(chrome_options=options)


print('Fetching page. Be patient...')
browser.get('http://dart.fss.or.kr/')
browser.find_element_by_css_selector('#textCrpNm').send_keys('한국가스공사')
browser.find_element_by_css_selector('#date7').click()

browser.find_element_by_css_selector('#searchForm > fieldset > p.mb15 > a:nth-child(9)').click()
browser.find_element_by_css_selector('#publicType46').click()
browser.find_element_by_css_selector('#searchForm > fieldset > p.btn > input').click()
time.sleep(1)

browser.find_element_by_css_selector('#maxResultsCb').click()
'''
add into parser arg
'''
browser.find_element_by_css_selector('#maxResultsCb > option:nth-child(4)').click()
browser.find_element_by_css_selector('#searchpng').click()
time.sleep(2)

buttons = browser.find_elements_by_css_selector("[title^='Sales (Provisional) Performance (Fair Disclosure) Disclosure Viewer']")
print([b.get_attribute('title') for b in buttons])
link=[]
translator = Translator()

for button in buttons :
    link.append(button.get_attribute('href'))


    

df_total = pd.DataFrame()  
for li in link:

    browser.get(li)
    browser.implicitly_wait(15)
    browser.switch_to.frame('ifrm')
    table = browser.find_element_by_css_selector('#XFormD1_Form0_RepeatTable0')
    tr = table.find_elements_by_css_selector('tbody > tr')
    dateThis = browser.find_element_by_css_selector('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-child(20) > td:nth-child(2) > span').text
    res = [list(map(lambda td: td.text, tr[nth].find_elements_by_tag_name('td'))) for nth in range(12, 17)]
    df = pd.DataFrame(np.array(res))
    df.columns = df.iloc[0]
    df = df.iloc[1:]
    date = df.columns[1]
    date = date.replace('월','')
    position = date.index('.')
    position2 = date.index(')')
    date = date[position-2:position]+'/'+date[position+1:position2]
    date = datetime.strptime(date,'%y/%m')
    df = df.iloc[[0,1,3],[1]]
    df = df.T
    df.columns=['City gas',
    'Power generation',
    'Total']
    df.index=[date]
    df['Unit'] = ['1000 tonnes']
    df['City gas'].replace(',','', regex=True, inplace=True)
    df['City gas']=pd.to_numeric(df['City gas'],errors='coerce')
    df['Power generation'].replace(',','', regex=True, inplace=True)
    df['Power generation']=pd.to_numeric(df['Power generation'],errors='coerce')
    df['Total'].replace(',','', regex=True, inplace=True)
    df['Total']=pd.to_numeric(df['Total'],errors='coerce')
    df_total = df_total.append(df)
    
    
sql.write(df_total, table_name = 'Kogas_LNG_Monthly_Sales', schema = 'intern', if_exists='replace')




#####update only




print('Fetching page. Be patient...')
browser.get('http://dart.fss.or.kr/')
browser.find_element_by_css_selector('#textCrpNm').send_keys('한국가스공사')
browser.find_element_by_css_selector('#date2').click()

browser.find_element_by_css_selector('#searchForm > fieldset > p.mb15 > a:nth-child(9)').click()
browser.find_element_by_css_selector('#publicType46').click()
browser.find_element_by_css_selector('#searchForm > fieldset > p.btn > input').click()
time.sleep(1)

browser.find_element_by_css_selector('#maxResultsCb').click()
'''
add into parser arg
'''
browser.find_element_by_css_selector('#maxResultsCb > option:nth-child(4)').click()
browser.find_element_by_css_selector('#searchpng').click()
time.sleep(2)

buttons = browser.find_elements_by_css_selector("[title^='Sales (Provisional) Performance (Fair Disclosure) Disclosure Viewer']")
print([b.get_attribute('title') for b in buttons])
link=[]
translator = Translator()

for button in buttons :
    link.append(button.get_attribute('href'))


    

df_total = pd.DataFrame()  
for li in link:

    browser.get(li)
    browser.implicitly_wait(15)
    browser.switch_to.frame('ifrm')
    table = browser.find_element_by_css_selector('#XFormD1_Form0_RepeatTable0')
    tr = table.find_elements_by_css_selector('tbody > tr')
    dateThis = browser.find_element_by_css_selector('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-child(20) > td:nth-child(2) > span').text
    res = [list(map(lambda td: td.text, tr[nth].find_elements_by_tag_name('td'))) for nth in range(12, 17)]
    df = pd.DataFrame(np.array(res))
    df.columns = df.iloc[0]
    df = df.iloc[1:]
    date = df.columns[1]
    date = date.replace('월','')
    position = date.index('.')
    position2 = date.index(')')
    date = date[position-2:position]+'/'+date[position+1:position2]
    date = datetime.strptime(date,'%y/%m')
    df = df.iloc[[0,1,3],[1]]
    df = df.T
    df.columns=['City gas',
    'Power generation',
    'Total']
    df.index=[date]
    df['Unit'] = ['1000 tonnes']
    df['City gas'].replace(',','', regex=True, inplace=True)
    df['City gas']=pd.to_numeric(df['City gas'],errors='coerce')
    df['Power generation'].replace(',','', regex=True, inplace=True)
    df['Power generation']=pd.to_numeric(df['Power generation'],errors='coerce')
    df['Total'].replace(',','', regex=True, inplace=True)
    df['Total']=pd.to_numeric(df['Total'],errors='coerce')
    df_total = df_total.append(df)
    

    
    
query_Kogas=f'''SELECT *
  FROM [GlobalAnalystsSandbox].[intern].[Kogas_LNG_Monthly_Sales]'''

df_previous = sql.read(query_Kogas, schema='intern', type='query')

df_max =df_previous['Date'].max()
df_update = df_total[df_total['Date']>df_max]

sql.write(df_update, table_name = 'Kogas_LNG_Monthly_Sales', schema = 'intern', if_exists='append')