
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from glencorepy.data import sql
import datetime as dt
import re
import numpy as np
from datetime import date, datetime, timedelta
import re

#Checking from database to compare.
#update if the table is changed

# query_nuclear=f'''SELECT *
#   FROM [GlobalAnalystsSandbox].[intern].[Korea_nuclear_maintenance]'''

# df_ori = sql.read(query_nuclear, schema='intern', type='query')


def Clean_start(Rename): 
    # Search for opening bracket in the name followed by 
    # any characters repeated any number of times 
    if re.search('\~.*', Rename): 
  
        # Extract the position of beginning of pattern 
        pos = re.search('\~.*', Rename).start() 
        start = Rename[:pos]
        start = start.replace('.',' ').split(' ')
        startDate = date(int(start[0]),int(start[1]),int(start[2]))
        # return the cleaned name 
        return startDate 
  
    else: 
        # if clean up needed return the same name 
        return Rename
    
def Clean_end(Rename): 
    # Search for opening bracket in the name followed by 
    # any characters repeated any number of times 
    if re.search('\~.*', Rename): 
  
        # Extract the position of beginning of pattern 
        pos = re.search('\~.*', Rename).start() 
        end = Rename[pos+2:]
        end = end.replace('.',' ').split(' ')
        endDate = date(int(end[0]),int(end[1]),int(end[2]))
        return endDate
  
    else: 
        # if clean up needed return the same name 
        return Rename

options = Options()

list=['http://www.khnp.co.kr/front/plan/main.do?mnCd=FN05040701',
        'http://www.khnp.co.kr/front/plan/main2.do?mnCd=FN05040702',
        'http://www.khnp.co.kr/front/plan/main3.do?mnCd=FN05040703',
        'http://www.khnp.co.kr/front/plan/main4.do?mnCd=FN05040704',
        'http://www.khnp.co.kr/front/plan/main5.do?mnCd=FN05040705']


browser = webdriver.Chrome(chrome_options=options)

df_total = pd.DataFrame()

for url in list:
    
    browser.get(url)
    
    soup = BeautifulSoup(browser.page_source, features='lxml')
    tables = soup.findAll('table', attrs={ 'class': 'tbl col row' })
    title = soup.findAll('h2', attrs={ 'class': 'tit dep02' })
    
    for i in range(0,len(tables)-1):
        table = tables[i]
        headers = [ header.text.strip() for header in table.find_all('th') ]

        rows = []
        for row in table.find_all('tr'):
            rows.append([ val.text.strip() for val in row.find_all('td') ])


        data = []
        data.append(headers)
        row_number = len(rows)
        for row in rows:
            data.append(row)

        df = pd.DataFrame(data)
        df = df.iloc[2:,[0,1,2]]
        df.columns=['Date','Degree','Days']
        df['Unit']=title[i].text
        df_total=df_total.append(df)

df_total = df_total.replace('',np.nan, regex=True)
df_total = df_total.dropna()
df_total['start_date'] = df_total['Date'].apply(Clean_start)
df_total['end_date'] = df_total['Date'].apply(Clean_end)
#delete useless title
dfn=df_total.iloc[:, 1:]
cols = dfn.columns.tolist()
#shift the order of the columns
cols = cols[-2:] + cols[:-2]
dfn = dfn[cols]

mapping = {
    '고리':'Kori',
    '한빛':'Hanbit',
    '한울':'Hanul',
    '월성':'Wolsong',
    '신':'Shin ',
    '호기':'Unit'
}

def mapK(s):
    for k, v in mapping.items():
        s=s.replace(k,v)
    return s

dfn.Unit = dfn.Unit.apply(lambda X :  mapK(X))
dfn['start_date'] = pd.to_datetime(dfn['start_date'])
dfn['end_date'] = pd.to_datetime(dfn['end_date'])

query_nuclear=f'''SELECT * FROM [GlobalAnalystsSandbox].[intern].[Korea_nuclear_maintenance]'''
df_ori = sql.read(query_nuclear, schema='intern', type='query')
dfN = df_ori.append(dfn)
dfN.drop_duplicates(inplace=True) 
sql.write(dfN, table_name = 'Korea_nuclear_maintenance'  ,schema='intern', if_exists='replace')

browser.quit()
EMAIL_RECIPIENTS = 'Juan.Chen@glencore.com.sg'
email.send_email(EMAIL_RECIPIENTS, f'Korea_nuclear - {date.today()}', 'Korea_nuclear_maintenance Parsing is done successfully')


if(not dfN.equals(df_ori)):
    EMAIL_RECIPIENTS = 'tony.zhu@glencore.com.sg'
    email.send_email(EMAIL_RECIPIENTS, f'Korea_nuclear - {date.today()}', 'There is an update on Korea_nuclear_maintenance. Parsing is done successfully')

