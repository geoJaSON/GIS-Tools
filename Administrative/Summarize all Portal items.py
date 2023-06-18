#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from arcgis.mapping import WebScene


# In[2]:


df = pd.DataFrame(columns = ['Name', 'Owner','Summary','Description','Tags','Type','ItemID','Access','Size','Views_6M','View_2M','Views_1M','Web_Maps','Credit_Consumption','Credits']) 


# In[3]:


df['Web_Maps']= df['Web_Maps'].astype(str)


# In[4]:


def credits(flt,size):
    if flt == 'Feature Service':
        usage = (size/10)*2.4
    else:
        usage = (size/1200)*1.2
    return(usage)


# In[5]:


from arcgis.gis import GIS
gis = GIS("home")
from arcgis.mapping import WebMap
from IPython.display import display


# In[ ]:


get_ipython().run_cell_magic('capture', '', 'from tqdm import tqdm_notebook as tqdm\ntqdm().pandas()')


# In[ ]:


webmap_search = gis.content.search('',item_type="Web Map",max_items=500)
search_my_contents = gis.content.search('',max_items=5000)
webscene_search = gis.content.search('',item_type="Web Scene",max_items=500)


# In[ ]:


for item in tqdm(search_my_contents):
    try:
        returnlist = []
        try:
            view6=item.usage("6M",as_df=True)['Usage'].sum()
            view3=item.usage("60D",as_df=True)['Usage'].sum()
            view1=item.usage("30D",as_df=True)['Usage'].sum()
        except:
            pass
        cpm = credits(item.type, item.size*0.000001)

        df=df.append({'Name':item.title, 'Owner':item.owner,'Description':item.description,'Tags':str(item.tags).strip("[").strip("]"),'Summary':item.snippet,'Type':item.type,'ItemID':item.id,'Access':item.access,'Web_Maps':'','Views_6M':view6,'View_2M':view3,'Views_1M':view1,'Size':item.size*0.000001,'Credits':item.accessInformation,'Credit_Consumption':cpm},ignore_index=True)
    except:
        pass


# In[ ]:


df = df.set_index('ItemID')


# In[ ]:


for nmap in tqdm(webmap_search):
    try:
        for layer in WebMap(nmap).layers:
            try:
                df.at[layer.itemId, 'Web_Maps'] = str(df.at[layer.itemId, 'Web_Maps'])+nmap.title+', '
            except Exception as e:
                pass
    except:
        pass


# In[ ]:


for nmap in tqdm(webscene_search):
    for layer in WebScene(nmap)['operationalLayers']:
        try:
            df.at[layer['itemId'], 'Web_Maps'] = str(df.at[layer['itemId'], 'Web_Maps'])+nmap.title+', '
        except:
            pass


# In[ ]:


df.to_csv(r'/arcgis/home/AGO_report.csv')


# In[ ]:




