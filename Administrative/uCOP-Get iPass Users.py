#!/usr/bin/env python
# coding: utf-8

# In[1]:


from arcgis.gis import GIS
import pandas as pd

tokens = pd.read_csv(r"C:\Users\M3ECHJJJ\Documents\Tokens.csv", index_col='Site')
gis = gis = GIS(tokens.at['uCOP Partners','URL'],token = tokens.at['uCOP Partners','Token'])


# In[2]:


users = gis.users.search(max_users=10000)


# In[13]:


df = pd.DataFrame(columns = ['Email','Username']) 


# In[14]:


for user in users:
    df=df.append({'Email':user.email,'Username':user.username},ignore_index=True)


# In[16]:


df.to_csv(r'D:/partners.csv')


# In[ ]:




