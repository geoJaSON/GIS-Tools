#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import smartsheet
from arcgis.gis import GIS
import datetime
import time
import pandas as pd


# In[2]:

tokens = pd.read_csv(r"C:\Users\M3ECHJJJ\Documents\Tokens.csv", index_col='Site')
token = tokens.at['SS Com OPM','Token']
smartsheet_client = smartsheet.Smartsheet(token)ty nrty nerty
sheet_id = tokens.at['SS Com OPM','ID']
sheet = smartsheet_client.Sheets.get_sheet(sheet_id)


# In[3]:


def simple_sheet_to_dataframe(sheet):
    col_names = [col.title for col in sheet.columns]
    rows = []
    for row in sheet.rows:
        cells = []
        for cell in row.cells:
            cells.append(cell.value)
        rows.append(cells)
    data_frame = pd.DataFrame(rows, columns=col_names)
    return data_frame
ss_df = simple_sheet_to_dataframe(sheet)


# In[2]:





# In[6]:


ss_df = simple_sheet_to_dataframe(sheet)


# In[7]:


rowList=[]
for row in doc["rows"]: #for each row in smartsheets
    newRow = {}
    value = "" #what does the empty quotes do?
    for col in range(0,37):
        try:
            col_id = int(row["cells"][col]["columnId"])
            col_title = column_id_to_title[col_id]
            value = row["cells"][col]["value"]
            newRow[col_title]=value
            #print(col,value)
        except Exception as e:
            #print("ERROR:",e,col,value)
            pass
    rowList.append(newRow)
print(len(rowList))
#rowList


# In[8]:


gis_url = tokens.at['SWD-EM','URL']       #### Add your username and password
gis_username = tokens.at['SWD-EM','Username']
gis_password = tokens.at['SWD-EM','Password']
gis = arcgis.gis.GIS(gis_url, gis_username,gis_password)


# In[242]:


import pandas as pd
layer_item = gis.content.get('e27948e0f56a4e4ca2b4204dfccfcb9d')
leave_item = gis.content.get('435053d9d57a4f1cbd3de34f1432f707')


# In[171]:


layers = layer_item.layers
fset=layers[0].query()
features = fset.features
flayer = layers[0]


# In[243]:


layers = leave_item.tables
fset=layers[0].query()
leave_features = fset.features
leave_flayer = layers[0]


# In[273]:


for f in features:
    attribute_dict = {}
    leaveList=[]
    for index, row in ss_df.iterrows():
        if row['Order'] == f.attributes['s_order']:
            data = {'Plans & Specs to CT':[row['Plans & Specs to CT']],
            'Bid_Opening':[row['Bid_Opening']],
            'Award':[row['Award']]}
            temp_df = pd.DataFrame(data,index =['col'])
            temp_df = temp_df.transpose()
            temp_df = temp_df.dropna()
            temp_df['col'] = temp_df['col'].astype('datetime64[D]')
            temp_df = temp_df[(temp_df['col'] >= datetime.datetime.now())]
            temp_df['col'] =pd.to_datetime(temp_df.col)
            temp_df.sort_values(by=['col'])
            attribute_dict['OBJECTID']=f.attributes['OBJECTID']
            for index_temp, row_temp in temp_df.iterrows():
                attribute_dict['nextdue'] = temp_df.index[0]
                attribute_dict['nextduedate'] = int(time.mktime((temp_df['col'].iloc[0]).timetuple())*1000+63200000)
                if (datetime.datetime.now()-temp_df['col'].iloc[0]).days >(-31):
                    attribute_dict['hexcolor1'] = 'ff0000'
                elif (datetime.datetime.now()-temp_df['col'].iloc[0]).days <(-30) and (datetime.datetime.now()-temp_df['col'].iloc[0]).days >(-90):
                    attribute_dict['hexcolor1'] = 'ffff00'
                else:
                    attribute_dict['hexcolor1'] = 'ffffff'
                try:
                    attribute_dict['upcoming1']=temp_df.index[1]
                    attribute_dict['upcoming1date']=int(time.mktime((temp_df['col'].iloc[1]).timetuple())*1000+63200000)
                    if (datetime.datetime.now()-temp_df['col'].iloc[1]).days >(-31):
                        attribute_dict['hexcolor2'] = 'ff0000'
                    elif (datetime.datetime.now()-temp_df['col'].iloc[1]).days <(-30) and (datetime.datetime.now()-temp_df['col'].iloc[1]).days >(-90):
                        attribute_dict['hexcolor2'] = 'ffff00'
                    else:
                        attribute_dict['hexcolor2'] = 'ffffff'
                except:
                    attribute_dict['upcoming1'] = ''
                    attribute_dict['upcoming1date']= None
                    attribute_dict['hexcolor2'] = 'ffffff'
                try:
                    attribute_dict['upcoming2']=temp_df.index[2]
                    attribute_dict['upcoming2date']=int(time.mktime((temp_df['col'].iloc[2]).timetuple())*1000+63200000)
                    if (datetime.datetime.now()-temp_df['col'].iloc[2]).days >(-31):
                        attribute_dict['hexcolor3'] = 'ff0000'
                    elif (datetime.datetime.now()-temp_df['col'].iloc[2]).days <(-30) and (datetime.datetime.now()-temp_df['col'].iloc[2]).days >(-90):
                        attribute_dict['hexcolor3'] = 'ffff00'
                    else:
                        attribute_dict['hexcolor3'] = 'ffffff'
                except:
                    attribute_dict['upcoming2'] = ''
                    attribute_dict['upcoming2date']= None
                    attribute_dict['hexcolor3'] = 'ffffff'
    leaveList = []
    leaveList2= []
    leaveList3= []
    try:
        for l in leave_features:
            if temp_df['col'].iloc[0] >= datetime.datetime.fromtimestamp(l.attributes['outdate']/1000) and temp_df['col'].iloc[0] < datetime.datetime.fromtimestamp(l.attributes['indate']/1000):
                leaveList.append(l.attributes['empname'])
            try:
                if temp_df['col'].iloc[1] >= datetime.datetime.fromtimestamp(l.attributes['outdate']/1000) and temp_df['col'].iloc[1] < datetime.datetime.fromtimestamp(l.attributes['indate']/1000):
                    leaveList2.append(l.attributes['empname'])
            except:
                pass
            try:
                if temp_df['col'].iloc[2] >= datetime.datetime.fromtimestamp(l.attributes['outdate']/1000) and temp_df['col'].iloc[2] < datetime.datetime.fromtimestamp(l.attributes['indate']/1000):
                    leaveList3.append(l.attributes['empname'])
            except:
                pass
        attribute_dict['absentees']=", ".join(leaveList)
        attribute_dict['absentees1']=", ".join(leaveList2)
        attribute_dict['absentees2']=", ".join(leaveList3)
    except:
        pass
    flayer.edit_features(updates=[{'attributes':attribute_dict}])


# In[8]:


ss_df


# In[ ]:
