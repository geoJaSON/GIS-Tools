#!/usr/bin/env python
# coding: utf-8

# In[40]:


import pandas as pd
import arcgis as arcgis
import json
import urllib.request as request
from arcgis import geometry


# In[26]:


get_ipython().run_cell_magic('capture', '', 'from tqdm import tqdm_notebook as tqdm\ntqdm().pandas()')


# In[35]:


print('Prepping Geocoder')
def geocode(addressLine):
    try:
        addressLine = addressLine.replace(' ','%20')
        with request.urlopen(r'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?Address=' + addressLine + '&outFields=*&forStorage=false&f=pjson') as response:
            source = response.read()
            data = json.loads(source)
        y1 = data['candidates'][0].get("location",{}).get("y")
        x1 = data['candidates'][0].get("location",{}).get("x")
        return x1, y1
    except Exception as e:
        return 0,0


# In[70]:


df = pd.read_excel (r"S:\Shared Files\Safety\Dashboard Data Files\FY21 SWG Accident Log.xlsx",'400 Contractor Employee Acc',keep_default_na=True)


# In[71]:


df = df.rename(columns=df.iloc[2])


# In[72]:


df = df[df['Accident Number'].notna()]
df = df.drop([2])
df = df.fillna('')


# In[23]:


tokens = pd.read_csv(r"C:\Users\M3ECHJJJ\Documents\Tokens.csv", index_col='Site')
gis = GIS(tokens.at['uCOP','URL'])

track_layer_item = gis.content.get('dd9f03f47837453d94983a45fd3d4f9e')
track_layers = track_layer_item.layers
track_fset=track_layers[0].query()
track_features = track_fset.features
track_flayer = track_layers[0]
track_flayer


# In[ ]:


def getValue(row)
    try:
    
    except:
        return


# In[ ]:





# In[76]:


for index, row in tqdm(df.iterrows(), total=df.shape[0]):
    attributes_dict = {}
    x,y = geocode(row['Location'])
    input_geometry = {'y':y,'x':x}
    #output_geometry = geometry.project(geometries = [input_geometry],in_sr = 4326, out_sr = 3857,gis = gis)
    attributes_dict['accident_number'] = row['Accident Number']
    #attributes_dict['date_of_accident'] = row['Date of Accident MM/DD/YYYY']
    attributes_dict['location'] = row['Location']
    attributes_dict['name'] = row['Name: L/F/M']
    attributes_dict['job_title'] = row['Job Title']
    attributes_dict['injury_type'] = row['Injury Type']
    #attributes_dict['construction_activity'] = row['']
    attributes_dict['accident_description'] = row['Accident Description']
    #attributes_dict['death'] = row['  Death']
    #attributes_dict['days_away'] = row['  Days Away (days)']
    #attributes_dict['job_transfer_or_restriction'] = row['  Job Transfer or   Restriction']
    #attributes_dict['medical_treatment_beyond'] = row['  Medical Treatment Beyond First Aid']
    #attributes_dict['days_away_from_work'] = row['  Days Away (days)']
    #attributes_dict['on_job_transfer_or_restriction'] = row['  Job Transfer or   Restriction']
    attributes_dict['contractor'] = row['Contractor']
    #attributes_dict['first_aid_only'] = row['First Aid Only (#1)']
    #attributes_dict['injury'] = row['  Injury']
    #attributes_dict['skin_disorder'] = row['  Skin Disorder']
    #attributes_dict['respiratory_condition'] = row['  Respiratory Condition']
    #attributes_dict['poisoning'] = row['  Poisoning']
    #attributes_dict['hearing_loss'] = row['  Hearing Loss']
    #attributes_dict['all_other_illnesses'] = row['  All Other Illnesses']
    #attributes_dict['osha_log_number'] = row['OSHA LOG NUMBER']
    #attributes_dict['posted_to_sharepoint'] = row['Posted to Share Point ']
    
    new_feature = {"attributes": attributes_dict,"geometry":input_geometry}
    track_flayer.edit_features(adds = [new_feature])


# In[69]:


track_flayer.edit_features(adds = [new_feature])


# In[68]:


new_feature


# In[ ]:




