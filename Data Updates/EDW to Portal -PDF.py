#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import arcgis as arcgis
from datetime import datetime, timedelta
from copy import deepcopy
import arcgis


# Path to xls file and number of days from beginning of report to end.

# In[5]:


xls_path = r"D:\01-Aug-2021-14-Aug-2021_Chargeability Report.xls"
report_extent =  timedelta(days=-13)


# In[6]:


df = pd.read_excel (xls_path,'Table 1',keep_default_na=True)
time_string = (df.columns[3]).split(' - ')[1][:11]
time_string =time_string.replace('\n','')
df=df.drop(df.index[[0,1]])
new_header = df.iloc[0]
df = df[1:]
df.columns = new_header
df = df.dropna(subset=['Employee'])
df = df.set_index('Employee')
df = df.drop(['Org Total:','Employee'])


# In[20]:


print(time_string.replace('\n',''))


# In[21]:


tokens = pd.read_csv(r"C:\Users\M3ECHJJJ\Documents\Tokens.csv", index_col='Site')
gis = GIS(tokens.at['uCOP','URL'])
layer_item = gis.content.get('dc62eba7583d438ea354a7c35311be94')
layers = layer_item.layers
fset=layers[0].query()
features = fset.features
flayer = layers[0]
flayer


# In[22]:


sixhours = timedelta(hours=12)
pp_end = datetime.strptime(time_string, '%d-%b-%Y')+sixhours
pp_start = pp_end + report_extent


# In[23]:


import time


# In[24]:


ago_pp_end = int(time.mktime(pp_end.timetuple()))*1000
ago_pp_start = int(time.mktime(pp_start.timetuple()))*1000


# In[25]:


df.to_csv(r'D:\report.csv')


# In[34]:


for index, row in df.iterrows():
    try:
        index = index.split(' ')
        name = index[1]+' '+index[0].replace(',','')
        name = name.title()
        t_feature = [f for f in features if f.attributes['name']==name][0]
        t_feature.attributes['cross_charge'] = row['Cross-\nCharge']
        t_feature.attributes['civil'] = row['Civil']
        t_feature.attributes['military'] = row['Military']
        t_feature.attributes['doh'] = row['DOH']
        t_feature.attributes['facility'] = row['Facility']
        t_feature.attributes['g_a'] = row['G&A']
        t_feature.attributes['s_a'] = row['S&A']
        t_feature.attributes['area_offices'] = row['Area\nOffices']
        t_feature.attributes['total_hours'] = row['Total\nHours']
        t_feature.attributes['total_direct'] = row['Total\nDirect']
        t_feature.attributes['actual_direct'] = row['Actual\nDirect\nCharge Rate']        
        t_feature.attributes['budgeted_direct'] = row['Budgeted\nDirect\nCharge Rate']
        t_feature.attributes['variance'] = row['Variance\nActual/\nBudget']          
        #update_result = flayer.edit_features(updates=[t_feature])
        #update_result
        print(name,'Updated')
    except Exception as e:
        attributes={}
        attributes['name']=name
        attributes['org']=row['Org\nCode']
        attributes['cross_charge'] = row['Cross-\nCharge']
        attributes['civil'] = row['Civil']
        attributes['military'] = row['Military']
        attributes['doh'] = row['DOH']
        attributes['facility'] = row['Facility']
        attributes['g_a'] = row['G&A']
        attributes['s_a'] = row['S&A']
        attributes['area_offices'] = row['Area\nOffices']
        attributes['total_hours'] = row['Total\nHours']
        attributes['total_direct'] = row['Total\nDirect']
        attributes['actual_direct'] = row['Actual\nDirect\nCharge Rate']        
        attributes['budgeted_direct'] = row['Budgeted\nDirect\nCharge Rate']
        attributes['variance'] = row['Variance\nActual/\nBudget']          
        update_result = flayer.edit_features(adds=[{'attributes':attributes}])
        print(name, 'Added')


# Add report to historical table

# In[15]:


tables = layer_item.tables
fset=tables[0].query()
features = fset.features
flayer = tables[0]
flayer
original_feature = [f for f in features if f.attributes['objectid'] ==1][0]

feature_to_be_updated = deepcopy(original_feature)
template_feature = deepcopy(feature_to_be_updated)


# In[16]:


for index, row in df.iterrows():
    try:
        new_feature = deepcopy(template_feature)
        index = index.split(' ')
        name = index[1]+' '+index[0].replace(',','')
        name = name.title()
        new_feature.attributes['name'] = name
        new_feature.attributes['org'] = row['Org\nCode']
        new_feature.attributes['cross_charge'] = row['Cross-\nCharge']
        new_feature.attributes['civil'] = row['Civil']
        new_feature.attributes['military'] = row['Military']
        new_feature.attributes['doh'] = row['DOH']
        new_feature.attributes['facility'] = row['Facility']
        new_feature.attributes['g_a'] = row['G&A']
        new_feature.attributes['s_a'] = row['S&A']
        new_feature.attributes['area_offices'] = row['Area\nOffices']
        new_feature.attributes['total_hours'] = row['Total\nHours']
        new_feature.attributes['total_direct'] = row['Total\nDirect']
        new_feature.attributes['actual_direct'] = row['Actual\nDirect\nCharge Rate']        
        new_feature.attributes['budgeted_direct'] = row['Budgeted\nDirect\nCharge Rate']
        new_feature.attributes['variance'] = row['Variance\nActual/\nBudget']
        new_feature.attributes['pay_period_begin'] = ago_pp_start
        new_feature.attributes['pay_period_end'] = ago_pp_end
        update_result = flayer.edit_features(adds = [new_feature])
        update_result
    except Exception as e:
        print(e)


# In[8]:


df


# In[33]:


print(index)


# In[ ]:




