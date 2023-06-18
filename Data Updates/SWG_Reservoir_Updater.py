#!/usr/bin/env python
# coding: utf-8

# In[1]:
print('Importing Modules')

from arcgis.gis import GIS
import urllib.request
import json
import pandas as pd


# In[2]:
tokens = pd.read_csv(r"C:\Users\M3ECHJJJ\Documents\Tokens.csv", index_col='Site')

print('Connecting to Enterprise')
gis_url = tokens.at['SWD-EM','URL']       #### Add your username and password
gis_username = tokens.at['SWD-EM','Username']
gis_password = tokens.at['SWD-EM','Password']


# In[3]:


# connect to reservoir layer to update
res_layer_item = gis.content.get('21a0345467e14ab5ab92c65c281565b1')
res_layers = res_layer_item.layers
res_fset = res_layers[0].query()
res_features = res_fset.features
res_flayer = res_layers[0]

# connect to water surface extents to update
ext_layer_item = gis.content.get('a060446864bc44cca60f548cffd3f0ad')
ext_layers = ext_layer_item.layers

add_flayer = ext_layers[1]
bar_flayer = ext_layers[0]



# In[22]:

print('Fetching USGS Data')
# connect to USGS JSON service to pull data
url = 'https://waterservices.usgs.gov/nwis/iv/?format=json&sites=08072500,08073000&parameterCd=00054,62615&siteStatus=all'
with urllib.request.urlopen(url) as url:
    data = json.loads(url.read().decode())
url = 'https://waterservices.usgs.gov/nwis/iv/?format=json&sites=08073100,08072600&parameterCd=00060&siteStatus=all'
with urllib.request.urlopen(url) as url:
    data2 = json.loads(url.read().decode())


# In[23]:


# shift all historical elevation values one cell to the right (stores last 24 hours of data very 15 minutes)
# elevation24_4 takes the value of elevation24_3 and so on
def shift_elevation_values():
    for index, row in df.iterrows():
        for i in reversed(range(1, 25)):
            for n in reversed(range(1, 5)):
                try:
                    if i == 1 and n == 1:
                        df.at[index, 'elevation1_1'] = row['elevation']
                    elif i != 1 and n == 1:
                        df.at[index, 'elevation' + str(i) + '_' + str(
                            n)] = row['elevation' + str(i - 1) + '_' + str(4)]
                    else:
                        df.at[index, 'elevation' + str(i) + '_' + str(
                            n)] = row['elevation' + str(i) + '_' + str(n - 1)]
                except:
                    pass


# In[24]:


# Get values out of the JSON pulled from USGS, 08072500 is Barker, 08072500 is Addicks
def update_values_from_usgs():
    df.at['08072500', 'storage'] = data['value']['timeSeries'][0]['values'][0]['value'][0]['value']
    df.at['08072500', 'elevation'] = data['value']['timeSeries'][1]['values'][0]['value'][0]['value']
    df.at['08073000', 'storage'] = data['value']['timeSeries'][2]['values'][0]['value'][0]['value']
    df.at['08073000', 'elevation'] = data['value']['timeSeries'][3]['values'][0]['value'][0]['value']
    df.at['08072500', 'flow'] = data2['value']['timeSeries'][0]['values'][0]['value'][0]['value']
    df.at['08073000', 'flow'] = data2['value']['timeSeries'][1]['values'][0]['value'][0]['value']


# In[25]:


# Calc the change in elevation in the last 15 minutes (last update)
def calc_change_in_elev():
    for index, row in df.iterrows():
        df.at[index, 'elevchange'] = row['elevation'] - row['elevation1_1']


# In[26]:


# Set the stage of the reservoirs depending on the elevations in their stage attributes
def set_status():
    for index, row in df.iterrows():
        if row['elevation'] >= row['stage1elev'] and row['elevation'] < row['stage2elev']:
            df.at[index, 'stage'] = 'Stage 1'
        elif row['elevation'] >= row['stage2elev']:
            df.at[index, 'stage'] = 'Stage 2'
        else:
            df.at[index, 'stage'] = 'Normal Stage'


# In[27]:

print('Processing Data')
# Create dataframe out of last updated AGOL reservoir layer.
df = res_flayer.query().sdf
df = df.set_index('usgsid')


# In[28]:


# Go through columns and make sure they all are floats, else risks being integer and erroring out if a decimal gets placed in.
for i in range(1, 25):
    for n in range(1, 5):
        df['elevation' + str(i) + '_' + str(n)] = pd.to_numeric(
            df['elevation' + str(i) + '_' + str(n)], downcast="float")
df["storage"] = pd.to_numeric(df["storage"], downcast="float")
df["elevation"] = pd.to_numeric(df["elevation"], downcast="float")
df["elevchange"] = pd.to_numeric(df["elevchange"], downcast="float")
df['flow'] = pd.to_numeric(df['flow'], downcast="float")


# In[29]:


# Run the above functions and update values into the dataframe
try:
    shift_elevation_values() #Move elevation values to fields immediately to left to shift hydrograph
    update_values_from_usgs() #Get updated USGS gauge values
    calc_change_in_elev() #Calc change in elevation based on previous value
    set_status() #Define the alert level based on elevation
    # trigger_emails()
except Exception as e:
    print(e)


# In[30]:


# list of all columns in the dataframe to push to AGOL
column_list_to_update = ['objectid', 'elevation', 'flow', 'elevchange', 'stage', 'storage', 'elevation1_1', 'elevation1_2', 'elevation1_3', 'elevation1_4', 'elevation2_1', 'elevation2_2', 'elevation2_3', 'elevation2_4', 'elevation3_1', 'elevation3_2', 'elevation3_3', 'elevation3_4', 'elevation4_1', 'elevation4_2', 'elevation4_3', 'elevation4_4', 'elevation5_1', 'elevation5_2', 'elevation5_3', 'elevation5_4', 'elevation6_1', 'elevation6_2', 'elevation6_3', 'elevation6_4', 'elevation7_1', 'elevation7_2', 'elevation7_3', 'elevation7_4', 'elevation8_1', 'elevation8_2', 'elevation8_3', 'elevation8_4', 'elevation9_1', 'elevation9_2', 'elevation9_3', 'elevation9_4', 'elevation10_1', 'elevation10_2', 'elevation10_3', 'elevation10_4', 'elevation11_1', 'elevation11_2', 'elevation11_3', 'elevation11_4', 'elevation12_1', 'elevation12_2',
                         'elevation12_3', 'elevation12_4', 'elevation13_1', 'elevation13_2', 'elevation13_3', 'elevation13_4', 'elevation14_1', 'elevation14_2', 'elevation14_3', 'elevation14_4', 'elevation15_1', 'elevation15_2', 'elevation15_3', 'elevation15_4', 'elevation16_1', 'elevation16_2', 'elevation16_3', 'elevation16_4', 'elevation17_1', 'elevation17_2', 'elevation17_3', 'elevation17_4', 'elevation18_1', 'elevation18_2', 'elevation18_3', 'elevation18_4', 'elevation19_1', 'elevation19_2', 'elevation19_3', 'elevation19_4', 'elevation20_1', 'elevation20_2', 'elevation20_3', 'elevation20_4', 'elevation21_1', 'elevation21_2', 'elevation21_3', 'elevation21_4', 'elevation22_1', 'elevation22_2', 'elevation22_3', 'elevation22_4', 'elevation23_1', 'elevation23_2', 'elevation23_3', 'elevation23_4', 'elevation24_1', 'elevation24_2', 'elevation24_3', 'elevation24_4']


# In[31]:

print('Pushing Data to AGOL')
# push updated dataframe to AGOL
for index, row in df.iterrows():
    attributes_dict = {}
    for col in column_list_to_update:
        attributes_dict[col] = row[col]
    updates_to_push = {"attributes": attributes_dict}
    update_result = res_flayer.edit_features(updates=[updates_to_push])

print('Lakes updated')


#Connect to the water surface extent polygon feature layer, toggle all to diplay to "no" and set polygons equal to the current elevation to "yes"
bar_fset = ext_layers[0].query()
bar_features = bar_fset.features
add_fset = ext_layers[1].query()
add_features = add_fset.features

bar_updates_to_push = []
add_updates_to_push = []

print('Updating Extents')

for f in bar_features:
    if int(f.attributes['poolelevat']) == int(df.iloc[1]['elevation']):
        bar_updates_to_push.append({'attributes':{'fid':f.attributes['fid'],'current_extent':'yes'}})
    else:
        bar_updates_to_push.append({'attributes':{'fid':f.attributes['fid'],'current_extent':'no'}})

for f in add_features:
    if int(f.attributes['poolelevat']) == int(df.iloc[0]['elevation']):
        add_updates_to_push.append({'attributes':{'fid':f.attributes['fid'],'current_extent':'yes'}})
    else:
        add_updates_to_push.append({'attributes':{'fid':f.attributes['fid'],'current_extent':'no'}})

update_result = add_flayer.edit_features(updates=add_updates_to_push)
update_result = bar_flayer.edit_features(updates=bar_updates_to_push)
