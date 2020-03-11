# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 14:25:37 2020

@author: cnj
"""

import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import datetime as dt
import re
import numpy as np
from datetime import date, datetime, timedelta
import argparse
from dateutil import relativedelta


monthDict={1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
#month


options = Options()
options.headless = True
browser = webdriver.Chrome(chrome_options=options)

def find_all_indexes(input_str, search_str):
    l1 = []
    length = len(input_str)
    index = 0
    while index < length:
        i = input_str.find(search_str, index)
        if i == -1:
            return l1
        l1.append(i)
        index = i + 1
    return l1

def parse_month_year(yy, mm):
    
    #yy = args['year']
    #mm = args['month']
    keys = yy +'年'+ mm + '月份天然气运行简况'
    browser.get('https://so.ndrc.gov.cn/s?siteCode=bm04000007&token=&qt='+keys)
    
    tinow = browser.find_element_by_css_selector('body > div.container.clear_both > div.query_le.clear_both > ul > li:nth-child(1) > h2 > a')
    
    if keys not in tinow.get_attribute('title') : 
        print('Havent update any') 
        exit(1)
    
    tinow.click()

    print('Fetching page. Be patient...')
    browser.implicitly_wait(10)
    element = browser.find_element_by_css_selector('body > div.container > div.article > div.article_l > div.article_con.article_con_title')
    para = str(element.text)

    title = browser.find_element_by_css_selector('body > div.container > div.article > div.article_l > h2').text

    production_li = find_all_indexes(para, '天然气产量')
    import_li = find_all_indexes(para, '天然气进口量')
    consume_li = find_all_indexes(para, '天然气表观消费量')
    unit_li = find_all_indexes(para, '亿立方米')

    final_list = [para[int(production_li[0])+5:int(unit_li[0])],
                para[int(import_li[0])+6:int(unit_li[1])],
                para[int(consume_li [0])+8:int(unit_li[2])]]




    '''              
    print(para[int(production_li[1])+5:int(unit_li[3])])
    print(para[int(import_li[0])+6:int(unit_li[1])])
    print(para[int(import_li[1])+6:int(unit_li[4])])
    print(para[int(consume_li [0])+8:int(unit_li[2])])
    print(para[int(consume_li [1])+8:int(unit_li[5])])
    '''

    title = browser.find_element_by_css_selector('body > div.container > div.article > div.article_l > h2').text
    Ymonth = str(title).replace('年',' ').replace('月',' ').replace('日','').replace('-',' ').split(' ')
    timestamp = date(int(Ymonth[0]),int(Ymonth[1]),int(1))
    timestamp 
    df = pd.DataFrame(np.array(final_list))
    df.columns=['Value']
    df['time']=timestamp 
    df['Name']=['production','import','consume']
    df['Unit']='100 million cubic meters'
    df['Source']='Economic Operation Regulation Bureau'
    df.index=df.time

    
def parse_month_year_Infra(yy, mm):
    
    
    keys = yy +'年'+ mm + '月份天然气情况'
    browser.get('https://so.ndrc.gov.cn/s?siteCode=bm04000007&token=&qt='+keys)
    
    tinow = browser.find_element_by_css_selector('body > div.container.clear_both > div.query_le.clear_both > ul > li:nth-child(1) > h2 > a')
    
    if keys not in tinow.get_attribute('title') : 
        print('Havent update any') 
        exit(0)
    
    url = str(tinow.get_attribute('href'))
    browser.get(url)

    print('Fetching page. Be patient...')
    browser.implicitly_wait(13)
    element = browser.find_element_by_css_selector('body > div.container > div.article > div.article_l > div.article_con.article_con_title')
    para = str(element.text)

    title = browser.find_element_by_css_selector('body > div.container > div.article > div.article_l > h2').text

    production_li = find_all_indexes(para, '天然气产量')
    import_li = find_all_indexes(para, '天然气进口量')
    consume_li = find_all_indexes(para, '天然气表观消费量')
    unit_li = find_all_indexes(para, '亿立方米')

    final_list = [para[int(production_li[0])+5:int(unit_li[0])],
                para[int(import_li[0])+6:int(unit_li[1])],
                para[int(consume_li [0])+8:int(unit_li[2])]]




    '''              
    print(para[int(production_li[1])+5:int(unit_li[3])])
    print(para[int(import_li[0])+6:int(unit_li[1])])
    print(para[int(import_li[1])+6:int(unit_li[4])])
    print(para[int(consume_li [0])+8:int(unit_li[2])])
    print(para[int(consume_li [1])+8:int(unit_li[5])])
    '''

    title = browser.find_element_by_css_selector('body > div.container > div.article > div.article_l > h2').text
    Ymonth = str(title).replace('年',' ').replace('月',' ').replace('日','').replace('-',' ').split(' ')
    timestamp = date(int(Ymonth[0]),int(Ymonth[1]),int(1))
    timestamp 
    df = pd.DataFrame(np.array(final_list))
    df.columns=['Value']
    df['time']=timestamp 
    df['Name']=['production','import','consume']
    df['Unit']='100 million cubic meters'
    df['Source']='Infrastructure Development Division'
    df.index=df.time
    


df = pd.DataFrame()
for yy in range(2018,2020):
    for mm in range(1,13):
        parse_month_year(yy,mm)

