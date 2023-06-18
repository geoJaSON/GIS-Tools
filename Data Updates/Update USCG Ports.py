#%%
import os, tokens
#%%

driverpath = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Documents','chromedriver.exe')

from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas as pd
pd.set_option('display.max_rows', None)
from arcgis.gis import GIS
import numpy as np
from win32api import *

url = 'https://homeport.uscg.mil/port-directory/'
xpath= "/html/body/form/div[12]/div[2]/div[2]/div[2]/div[3]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div[2]/div[1]/div/div/div[2]/div/div[2]/div/table"

#%%
directories = {"boston":"0","buffalo-(buffalo-and-cleveland)":"5","charleston":"5","columbia-river":"0",
"corpus-christi":"4","d8-gulf-of-mexico":"0","delaware-bay":"0","detroit":"0","duluth":"4","guam":"0","honolulu":"0","houma":"5","houston-galveston":"0",
"jacksonville":"0","key-west":"5","lake-michigan":"5","long-island-sound":"4","los-angeles-long-beach":"5","lower-mississippi-river-(memphis)":"5","maryland-ncr":"0","miami":"0","mobile":"4","new-orleans":"0","new-york":"0","north-carolina":"4","northern-new-england-(portland-maine)":"0","ohio-valley":"4","pittsburgh":"0","port-arthur-and-lake-charles":"0","prince-william-sound-(valdez)":"4","san-diego":"0","san-francisco":"6","san-juan":"5","sault-ste-marie":"4","savannah":"0","seak-southeast-alaska-(juneau)":"4","seattle-(puget-sound)":"4","southeastern-new-england-(providence)":"0","st-petersburg":"4","upper-mississippi-river-(st-louis)":"7","virginia":"0","western-alaska-(anchorage)": "9"}

urlToSite= {"boston":"Boston",
"buffalo-(buffalo-and-cleveland)":"Buffalo",
"charleston":"Charleston",
"columbia-river":"Columbia River",
"corpus-christi":"Corpus Christi",
"d8-gulf-of-mexico":"D8 Gulf of Mexico",
"delaware-bay":"Delaware Bay",
"detroit":"Detroit",
"duluth":"Duluth",
"guam":"Guam",
"honolulu":"Honolulu",
"houma":"Houma",
"houston-galveston":"Houston-Galveston",
"jacksonville":"Jacksonville",
"key-west":"Key West",
"lake-michigan":"Lake Michigan",
"long-island-sound":"Long Island Sound",
"los-angeles-long-beach":"Los Angeles-Long Beach",
"lower-mississippi-river-(memphis)":"Lower Mississippi River",
"maryland-ncr":"Maryland-NCR",
"miami":"Miami",
"mobile":"Mobile",
"new-orleans":"New Orleans",
"new-york":"New York",
"north-carolina":"North Carolina",
"northern-new-england-(portland-maine)":"Northern New England",
"ohio-valley":"Ohio Valley",
"pittsburgh":"Pittsburgh",
"port-arthur-and-lake-charles":"Port Arthur and Lake Charles",
"prince-william-sound-(valdez)":"Prince William Sound",
"san-diego":"San Diego",
"san-francisco":"San Francisco",
"san-juan":"San Juan",
"sault-ste-marie":"Sault Ste. Marie",
"savannah":"Savannah",
"seak-southeast-alaska-(juneau)":"SEAK - Southeast Alaska",
"seattle-(puget-sound)":"Seattle",
"southeastern-new-england-(providence)":"Southeastern New England",
"st-petersburg":"St. Petersburg",
"upper-mississippi-river-(st-louis)":"Upper Mississippi River",
"virginia":"Virginia",
"western-alaska-(anchorage)": "Western Alaska"}

def get_version_number(file_path):

    File_information = GetFileVersionInfo(file_path, "\\")

    ms_file_version = File_information['FileVersionMS']
    ls_file_version = File_information['FileVersionLS']

    return [str(HIWORD(ms_file_version)), str(LOWORD(ms_file_version)),
            str(HIWORD(ls_file_version)), str(LOWORD(ls_file_version))]
#%%
file_path = r"C:\Users\g3retjjj\Downloads\chromedriver.exe"
driver = webdriver.Chrome(executable_path = driverpath)
df = pd.DataFrame(columns=['Port','Port Status','Comments','Last Changed','COTP'])
try:
    driver = webdriver.Chrome(executable_path = driverpath)
except:
    import urllib.request
    from zipfile import ZipFile
    downloadurl = f"https://chromedriver.storage.googleapis.com/{'.'.join(get_version_number(file_path))}/chromedriver_win32.zip"
    zipdownload = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads','chromedriver.zip')
    urllib.request.urlretrieve(downloadurl, zipdownload)
    with ZipFile(zipdownload, 'r') as zipObj:
        zipObj.extractall(os.path.dirname(driverpath))
    os.remove(zipdownload)
    driver = webdriver.Chrome(executable_path = driverpath)

for key,value in directories.items():
    print(key)
    urlpage = url+key
    driver.get(urlpage)
    time.sleep(10)
    #driver.Timeouts.ImplicitWait = 30000
    try:
        Button=driver.find_element("xpath", f'/html/body/form/div[12]/div[2]/div[2]/div[2]/div[3]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div[2]/div[1]/div/div/div[2]/div/div[3]/div[2]/div/ul/li[{value}]/a')
    except Exception as e:
        print(e)
    while(True):
        try:
            time.sleep(2)
            p_df = pd.read_html(driver.find_element("xpath", xpath).get_attribute('outerHTML'))[0]
            p_df['COTP'] = urlToSite[key]
            df = df.append(p_df)
            Button.click()
        except:
            break
driver.quit()

df = df.replace({np.nan: None})

#%%
gis = GIS(tokens.uCOP['url'])
port_layer_item = gis.content.get('e3fd7c2377c249f7af4ec2997e7fa707')

port_layers = port_layer_item.layers
port_fset=port_layers[0].query()
port_features = port_fset.features
port_flayer = port_layers[0]
feature_keys = {f.attributes['port'].upper(): f.attributes['objectid'] for f in port_features} #get objectids for counties

updates_to_push = []
adds_to_push = []

def assemble_updates(row):
    try:
        edit_feature = {'objectid': feature_keys[row['Port'].upper()]}
        edit_feature['condition'] = row['Port Status']
        edit_feature['comments'] = row['Comments']
        edit_feature['dateupdated'] = row['Last Changed']
        if row['Port Status'] == 'Open':
             edit_feature['color'] = '00c5ff'
        elif row['Port Status'] == 'Open with restrictions':
             edit_feature['color'] = 'A3FF73'
        elif row['Port Status'] == 'Whiskey':
             edit_feature['color'] = '00E600'
        elif row['Port Status'] == 'Yankee':
             edit_feature['color'] = 'FFFF00'
        elif row['Port Status'] == 'X-Ray':
             edit_feature['color'] = 'FF8000'
        elif row['Port Status'] == 'Zulu':
             edit_feature['color'] = 'FF0000'
        else :
             edit_feature['color'] = 'A1A1A1'
        feat = {'attributes': edit_feature}
        updates_to_push.append(feat)
    except KeyError:
        add_feature = {'port': row['Port']}
        add_feature['condition'] = row['Port Status']
        add_feature['comments'] = row['Comments']
        add_feature['sector'] = row['COTP']
        add_feature['dateupdated'] = row['Last Changed']
        if row['Port Status'] == 'Open':
             add_feature['color'] = '00c5ff'
        elif row['Port Status'] == 'Open with restrictions':
             add_feature['color'] = 'A3FF73'
        elif row['Port Status'] == 'Whiskey':
             add_feature['color'] = '00E600'
        elif row['Port Status'] == 'Yankee':
             add_feature['color'] = 'FFFF00'
        elif row['Port Status'] == 'X-Ray':
             add_feature['color'] = 'FF8000'
        elif row['Port Status'] == 'Zulu':
             add_feature['color'] = 'FF0000'
        else :
             add_feature['color'] = 'A1A1A1'
        feat = {'attributes': add_feature}
        adds_to_push.append(feat)



        #feat = {'geometry': {'x': row['loadlongitude'], 'y': row['loadlatitude']}, 'attributes': add_feature}


df.apply(lambda row: assemble_updates(row), axis=1)

update_result = port_flayer.edit_features(updates=updates_to_push, rollback_on_failure=False)
df.sort_values('Port')

# %%
