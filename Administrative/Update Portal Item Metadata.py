#!/usr/bin/env python
# coding: utf-8

# In[4]:


from arcgis.gis import GIS
gis = GIS("home")


# In[5]:


tagstoadd = ['United States Army Corps of Engineers', 'USACE', 'Galveston District', 'SWG']
creditstoadd = 'United States Army Corps of Engineers - Galveston District, Engineering and Construction, Geospatial Branch'
delim = ", "


# In[6]:


get_ipython().run_cell_magic('capture', '', 'from tqdm import tqdm_notebook as tqdm\ntqdm().pandas()')


# In[7]:


contents = gis.content.search('',max_items=5000)


# In[8]:


for item in tqdm(contents):
    try:
        tags_list = [*item.tags, *tagstoadd] 
        temp = list(map(str, tags_list)) 
        res = delim.join(temp)
        item.update(item_properties={'tags':str(res).title().replace('s2g','S2G').replace('Usace','USACE').replace('Swg','SWG').replace('Glo','GLO').replace('Mhrwa','MHRWA').replace('Nrda','NRDA').replace('Nps','NPS').replace('Dem','DEM').replace('Bbtrs','BBTRS')})
        item.update(item_properties={'accessInformation':'United States Army Corps of Engineers - Galveston District, Engineering and Construction, Geospatial Branch'})
    except:
        pass


# In[ ]:




