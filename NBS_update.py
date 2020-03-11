
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import datetime as dt
import re
import argparse


def Clean_names(Rename): 
    # Search for opening bracket in the name followed by 
    # any characters repeated any number of times 
    if re.search('\(.*', Rename): 
  
        # Extract the position of beginning of pattern 
        pos = re.search('\(.*', Rename).start() 
  
        # return the cleaned name 
        return Rename[:pos]
  
    else: 
        # if clean up needed return the same name 
        return Rename
    
def Clean_unit(Rename): 
    # Search for opening bracket in the name followed by 
    # any characters repeated any number of times 
    if re.search('\(.*', Rename): 

        # Extract the position of beginning of pattern 
        pos = re.search('\(.*', Rename).start() 

        # return the cleaned name 
        return Rename[pos:]
    

    
    
    
''' 
faster to get the map. If messy, I will save it to another file.
'''

data = '<ul id="treeZhiBiao_5_ul" class="level1 " style=""><li id="treeZhiBiao_9" class="level2" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_9_switch" title="" class="button level2 switch noline_open" treenode_switch=""></span><a id="treeZhiBiao_9_a" class="level2 curSelectedNode" treenode_a="" onclick="" target="_blank" style="" title="Output of Energy Products"><span id="treeZhiBiao_9_ico" title="" treenode_ico="" class="button ico_open" style=""></span>Output of Energy Products</span></a><ul id="treeZhiBiao_9_ul" class="level2 " style=""><li id="treeZhiBiao_10" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_10_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_10_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Coal"><span id="treeZhiBiao_10_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_10_span">Coal</span></a></li><li id="treeZhiBiao_11" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_11_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_11_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Crude oil"><span id="treeZhiBiao_11_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_11_span">Crude oil</span></a></li><li id="treeZhiBiao_12" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_12_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_12_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Natural Gas"><span id="treeZhiBiao_12_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_12_span">Natural Gas</span></a></li><li id="treeZhiBiao_13" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_13_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_13_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Coalbed Gas"><span id="treeZhiBiao_13_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_13_span">Coalbed Gas</span></a></li><li id="treeZhiBiao_14" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_14_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_14_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="LNG"><span id="treeZhiBiao_14_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_14_span">LNG</span></a></li><li id="treeZhiBiao_15" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_15_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_15_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Processing Volume of Crude oil"><span id="treeZhiBiao_15_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_15_span">Processing Volume of Crude oil</span></a></li><li id="treeZhiBiao_16" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_16_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_16_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Gasoline"><span id="treeZhiBiao_16_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_16_span">Gasoline</span></a></li><li id="treeZhiBiao_17" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_17_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_17_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Kerosene"><span id="treeZhiBiao_17_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_17_span">Kerosene</span></a></li><li id="treeZhiBiao_18" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_18_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_18_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Diesel Oil"><span id="treeZhiBiao_18_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_18_span">Diesel Oil</span></a></li><li id="treeZhiBiao_19" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_19_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_19_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Fuel Oil"><span id="treeZhiBiao_19_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_19_span">Fuel Oil</span></a></li><li id="treeZhiBiao_20" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_20_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_20_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Naphtha"><span id="treeZhiBiao_20_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_20_span">Naphtha</span></a></li><li id="treeZhiBiao_21" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_21_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_21_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="LPG"><span id="treeZhiBiao_21_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_21_span">LPG</span></a></li><li id="treeZhiBiao_22" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_22_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_22_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Petroleum Coke"><span id="treeZhiBiao_22_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_22_span">Petroleum Coke</span></a></li><li id="treeZhiBiao_23" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_23_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_23_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Asphalt"><span id="treeZhiBiao_23_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_23_span">Asphalt</span></a></li><li id="treeZhiBiao_24" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_24_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_24_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Coke"><span id="treeZhiBiao_24_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_24_span">Coke</span></a></li><li id="treeZhiBiao_25" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_25_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_25_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Electricity"><span id="treeZhiBiao_25_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_25_span">Electricity</span></a></li><li id="treeZhiBiao_26" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_26_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_26_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Thermal Power"><span id="treeZhiBiao_26_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_26_span">Thermal Power</span></a></li><li id="treeZhiBiao_27" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_27_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_27_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Hydro-electric Power"><span id="treeZhiBiao_27_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_27_span">Hydro-electric Power</span></a></li><li id="treeZhiBiao_28" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_28_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_28_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Nuclear Power"><span id="treeZhiBiao_28_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_28_span">Nuclear Power</span></a></li><li id="treeZhiBiao_29" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_29_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_29_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Wind Power"><span id="treeZhiBiao_29_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_29_span">Wind Power</span></a></li><li id="treeZhiBiao_30" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_30_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_30_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Solar power"><span id="treeZhiBiao_30_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_30_span">Solar power</span></a></li><li id="treeZhiBiao_31" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_31_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_31_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Gas"><span id="treeZhiBiao_31_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_31_span">Gas</span></a></li></ul></li></ul>'

result = re.findall(r'<span id="([A-Za-z0-9_]+)">([\w\s-]+)<',data)
spandict = {}
for a,b in result:
    spandict['#'+a]=b

spandict['#treeZhiBiao_15_span']='ProcessCrude'
spandict['#treeZhiBiao_22_span']='PetroCoke'
spandict['#treeZhiBiao_27_span']='Hydroelectri'
spandict['#treeZhiBiao_31_span']='Coalgas'
         
         
energy_list = list(spandict.keys())
energy_list=energy_list

province_list = {'110000':'Beijing','120000':'Tianjin','130000':'Hebei','140000':'Shanxi','150000':'Inner mongolia','210000':':Liaoning','220000':'Jilin','230000':'Heilongjiang',
         '310000':'Shanghai','320000':'Jiangsu','330000':'Zhejiang','340000':'Anhui','350000':'Fujian','360000':'Jiangxi','370000':'Shandong','410000':'Henan',
                 '420000':'Hubei','430000':'Hunan','440000':'Guangdong','450000':'Guangxi','460000':'Hainan','500000':'Chongqing','510000':'Sichuan','520000':'Guizhou','530000':'Yunnan','540000':'Tibet',
                 '610000':'shanxxi','620000':'Gansu','630000':'Qinghai','640000':'Ningxia','650000':'Xinjiang'}


list_pro = list(province_list.keys())



timeframe = str('2010-')

options = Options()
options.headless = True
browser = webdriver.Chrome()
print('Fetching page. Be patient...')
browser.get('http://data.stats.gov.cn/english/easyquery.htm?cn=E0101')
# select indicator
print('Mimicking clicks...')
browser.implicitly_wait(10)
indicator = browser.find_element_by_css_selector('#treeZhiBiao_5_span')
indicator.click()  
# TODO: use expected_conditions for waiting
print('Waiting for loading...')
print('Mimicking clicks...')
browser.implicitly_wait(10)
indicator = browser.find_element_by_css_selector('#treeZhiBiao_9_span')
indicator.click()
# TODO: use expected_conditions for waiting
print('Waiting for loading...')
print('Mimicking clicks...')
time.sleep(1)
flag=1
dd = []
df_all = pd.DataFrame(dd)  

for ee in energy_list[:2]:
    dd = []
    df_energy = pd.DataFrame(dd)
    indicator = browser.find_element_by_css_selector(ee)
    browser.implicitly_wait(10)
    indicator.click()
    # TODO: use expected_conditions for waiting
    if(flag) :
        dtHead = browser.find_element_by_css_selector('#mySelect_sj .dtHead')   
        dtHead.click()
        browser.find_element_by_css_selector('#mySelect_sj > div.dtHtml > div.dtBody > div.dtFoot > input').send_keys(timeframe)
        browser.find_element_by_css_selector('#mySelect_sj > div.dtHtml > div.dtBody > div.dtFoot > div.dtTextBtn.f10').click()
        flag=0

    # TODO: use expected_conditions for waiting
    print('Waiting for loading...')

    for pp in list_pro[:2]:

        dtHeadRegion = browser.find_element_by_css_selector('#mySelect_reg .dtHead')
        browser.implicitly_wait(10)
        dtHeadRegion.click()
        dt10 = browser.find_element_by_css_selector('#mySelect_reg .dtList li[code="' + pp + '"]')
        dt10.click()
        time.sleep(1)
        soup = BeautifulSoup(browser.page_source, features='lxml')
        table = soup.find('table', attrs={ 'class': 'public_table table_fix' })
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

        province_name = str(province_list.get(pp))
        province_col = [province_name for i in range(6)]

        energy_name = str(spandict.get(ee))
        energy_col = [energy_name for i in range(6)]
        df.columns = df.iloc[0]
        df = df[2:]
        col = list(df.Indicators)
        col.append('date')
        col.append('Energy')
        col.append('Province')
        dfn = df.T.iloc[1:-2]
        dfn.index = pd.to_datetime(dfn.index)
        dfn.index = dfn.index.strftime('%d-%m-%Y')        
        dfn['date'] = dfn.index
        dfn['Energy']=energy_name
        dfn['Province']=province_name
        dfn.columns=col
        cols = dfn.columns.tolist()
        cols = cols[-3:] + cols[:-3]
        dfn = dfn[cols]       
        df_energy = df_energy.append(dfn)

    df_energy = pd.melt(df_energy, id_vars=["date", "Energy","Province"], var_name="Report_name", value_name="Value")
    df_energy['Unit']=df_energy['Report_name'].apply(Clean_unit)
    df_energy['Report_name']=df_energy['Report_name'].apply(Clean_names)   
    df_all=df_all.append(df_energy)
    
df_all['Report_name'] = df_all['Report_name'].apply(lambda x : x.split(',')[1].strip())
df_all = df_all
df_all.Value.replace(',','', regex=True, inplace=True)
df_all.Value=pd.to_numeric(df_all['Value'],errors='raise')
df_all['date'] = pd.to_datetime(df_all['date'])
df_all['date']= df_all['date'].dt.strftime('%Y-%m-%d')
df_all['date'] = pd.to_datetime(df_all['date'])

sql.write(df_all, table_name = 'NBS_Total_china_monthly', schema='intern' ,if_exists='replace')










# aggregate stats from website
data = '<li id="treeZhiBiao_16" class="level2" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_16_switch" title="" class="button level2 switch noline_open" treenode_switch=""></span><a id="treeZhiBiao_16_a" class="level2" treenode_a="" onclick="" target="_blank" style="" title="Output of Energy Products"><span id="treeZhiBiao_16_ico" title="" treenode_ico="" class="button ico_open" style=""></spa>Output of Energy Products</span></a><ul id="treeZhiBiao_16_ul" class="level2 " style=""><li id="treeZhiBiao_17" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_17_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_17_a" class="level3 curSelectedNode" treenode_a="" onclick="" target="_blank" style="" title="Coal"><span id="treeZhiBiao_17_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_17_span">Coal</span></a></li><li id="treeZhiBiao_18" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_18_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_18_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Crude oil"><span id="treeZhiBiao_18_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_18_span">Crude oil</span></a></li><li id="treeZhiBiao_19" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_19_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_19_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Natural Gas"><span id="treeZhiBiao_19_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_19_span">Natural Gas</span></a></li><li id="treeZhiBiao_20" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_20_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_20_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Coalbed Gas"><span id="treeZhiBiao_20_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_20_span">Coalbed Gas</span></a></li><li id="treeZhiBiao_21" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_21_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_21_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="LNG"><span id="treeZhiBiao_21_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_21_span">LNG</span></a></li><li id="treeZhiBiao_22" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_22_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_22_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Processing Volume of Crude oil"><span id="treeZhiBiao_22_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_22_span">Processing Volume of Crude oil</span></a></li><li id="treeZhiBiao_23" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_23_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_23_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Gasoline"><span id="treeZhiBiao_23_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_23_span">Gasoline</span></a></li><li id="treeZhiBiao_24" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_24_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_24_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Kerosene"><span id="treeZhiBiao_24_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_24_span">Kerosene</span></a></li><li id="treeZhiBiao_25" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_25_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_25_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Diesel Oil"><span id="treeZhiBiao_25_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_25_span">Diesel Oil</span></a></li><li id="treeZhiBiao_26" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_26_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_26_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Fuel Oil"><span id="treeZhiBiao_26_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_26_span">Fuel Oil</span></a></li><li id="treeZhiBiao_27" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_27_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_27_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Naphtha"><span id="treeZhiBiao_27_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_27_span">Naphtha</span></a></li><li id="treeZhiBiao_28" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_28_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_28_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="LPG"><span id="treeZhiBiao_28_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_28_span">LPG</span></a></li><li id="treeZhiBiao_29" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_29_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_29_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Petroleum Coke"><span id="treeZhiBiao_29_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_29_span">Petroleum Coke</span></a></li><li id="treeZhiBiao_30" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_30_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_30_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Asphalt"><span id="treeZhiBiao_30_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_30_span">Asphalt</span></a></li><li id="treeZhiBiao_31" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_31_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_31_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Coke"><span id="treeZhiBiao_31_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_31_span">Coke</span></a></li><li id="treeZhiBiao_32" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_32_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_32_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Electricity"><span id="treeZhiBiao_32_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_32_span">Electricity</span></a></li><li id="treeZhiBiao_33" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_33_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_33_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Thermal Power"><span id="treeZhiBiao_33_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_33_span">Thermal Power</span></a></li><li id="treeZhiBiao_34" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_34_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_34_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Hydro-electric Power"><span id="treeZhiBiao_34_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_34_span">Hydro-electric Power</span></a></li><li id="treeZhiBiao_35" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_35_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_35_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Nuclear Power"><span id="treeZhiBiao_35_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_35_span">Nuclear Power</span></a></li><li id="treeZhiBiao_36" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_36_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_36_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Wind Power"><span id="treeZhiBiao_36_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_36_span">Wind Power</span></a></li><li id="treeZhiBiao_37" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_37_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_37_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Solar power"><span id="treeZhiBiao_37_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_37_span">Solar power</span></a></li><li id="treeZhiBiao_38" class="level3" tabindex="0" hidefocus="true" treenode=""><span id="treeZhiBiao_38_switch" title="" class="button level3 switch noline_docu" treenode_switch=""></span><a id="treeZhiBiao_38_a" class="level3" treenode_a="" onclick="" target="_blank" style="" title="Gas"><span id="treeZhiBiao_38_ico" title="" treenode_ico="" class="button ico_docu" style=""></span><span id="treeZhiBiao_38_span">Gas</span></a></li></ul></li>'

result = re.findall(r'<span id="([A-Za-z0-9_]+)">([\w\s-]+)<',data)

spandict = {}
for a,b in result:
    spandict['#'+a]=b

spandict['#treeZhiBiao_22_span']='processCrude'
spandict['#treeZhiBiao_29_span']='PetroCoke'
spandict['#treeZhiBiao_34_span']='hydroelectri'
spandict['#treeZhiBiao_38_span']='coalgas'


energy_list = list(spandict.keys())
energy_list=energy_list


print('Fetching page. Be patient...')
browser.get('http://data.stats.gov.cn/english/easyquery.htm?cn=A01')
# select indicator
print('Mimicking clicks...')
browser.implicitly_wait(10)
indicator = browser.find_element_by_css_selector('#treeZhiBiao_4_span')
indicator.click()  
# TODO: use expected_conditions for waiting
print('Waiting for loading...')
print('Mimicking clicks...')
browser.implicitly_wait(10)
indicator = browser.find_element_by_css_selector('#treeZhiBiao_16_span')
indicator.click()

# TODO: use expected_conditions for waiting
print('Waiting for loading...')
print('Mimicking clicks...')


browser.implicitly_wait(10)
dtHead = browser.find_element_by_css_selector('#mySelect_sj > div.dtHtml > div.dtHead')   
dtHead.click()
browser.find_element_by_css_selector('#mySelect_sj > div.dtHtml > div.dtBody > div.dtFoot > input').send_keys(timeframe)
browser.find_element_by_css_selector('#mySelect_sj > div.dtHtml > div.dtBody > div.dtFoot > div.dtTextBtn.f10').click()
dd = []
df_total = pd.DataFrame(dd)

for ee in energy_list[:3]:

    energy_name = str(spandict.get(ee))
    indicator = browser.find_element_by_css_selector(ee)
    indicator.click()
    time.sleep(1)
    # TODO: use expected_conditions for waiting
    print('Waiting for loading...')

    soup = BeautifulSoup(browser.page_source, features='lxml')
    table = soup.find('table', attrs={ 'class': 'public_table table_fix' })
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
    df.iloc[0]
    df.columns = df.iloc[0]
    df = df[2:]

    col = list(df.Indicators)
    dfn = df.T
    dfn = dfn.iloc[1:]
    dfn.index = pd.to_datetime(dfn.index)
    dfn.index = dfn.index.strftime('%Y-%m-%d')
    dfn.columns=col
    dfn['date'] = dfn.index
    dfn['Energy']=energy_name
    cols = dfn.columns.tolist()
    cols = cols[-2:] + cols[:-2]
    dfn = dfn[cols]
    dfn
    df1 = pd.melt(dfn, id_vars=["date", "Energy"], var_name="Report_name", value_name="Value")
    df_total = df_total.append(df1)

df_all = df_total   
df_all['Unit']=df_all['Report_name'].apply(Clean_unit)
df_all['Report_name']=df_all['Report_name'].apply(Clean_names)  
df_all['Report_name'] = df_all['Report_name'].apply(lambda x : x.split(',')[1].strip())
df_all.Value.replace(',','', regex=True, inplace=True)
df_all.Value=pd.to_numeric(df_all['Value'],errors='raise')
df_all['date'] = pd.to_datetime(df_all['date'])
df_all['date']= df_all['date'].dt.strftime('%Y-%m-%d')
df_all['date'] = pd.to_datetime(df_all['date'])

sql.write(df_all, table_name = 'NBS_Total_china_monthly', schema='intern' ,if_exists='replace')