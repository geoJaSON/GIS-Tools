#!/usr/bin/env python
# coding: utf-8

# ## Welcome to your notebook.
# 

# #### Run this cell to connect to your GIS and get started:

# In[1]:


from arcgis.gis import GIS
gis = GIS("",'','')
from arcgis.features import FeatureLayer


# In[2]:


track_layer_item = gis.content.get('')
track_layers = track_layer_item.layers
track_fset=track_layers[0].query()
track_features = track_fset.features
track_flayer = track_layers[0]


# In[3]:


new_field_names = ['elevation5_1','elevation5_2','elevation5_3','elevation5_4','elevation6_1','elevation6_2','elevation6_3','elevation6_4','elevation7_1','elevation7_2','elevation7_3','elevation7_4','elevation8_1','elevation8_2','elevation8_3','elevation8_4','elevation9_1','elevation9_2','elevation9_3','elevation9_4','elevation10_1','elevation10_2','elevation10_3','elevation10_4','elevation11_1','elevation11_2','elevation11_3','elevation11_4','elevation12_1','elevation12_2','elevation12_3','elevation12_4','elevation13_1','elevation13_2','elevation13_3','elevation13_4','elevation14_1','elevation14_2','elevation14_3','elevation14_4','elevation15_1','elevation15_2','elevation15_3','elevation15_4','elevation16_1','elevation16_2','elevation16_3','elevation16_4','elevation17_1','elevation17_2','elevation17_3','elevation17_4','elevation18_1','elevation18_2','elevation18_3','elevation18_4','elevation19_1','elevation19_2','elevation19_3','elevation19_4','elevation20_1','elevation20_2','elevation20_3','elevation20_4','elevation21_1','elevation21_2','elevation21_3','elevation21_4','elevation22_1','elevation22_2','elevation22_3','elevation22_4','elevation23_1','elevation23_2','elevation23_3','elevation23_4','elevation24_1','elevation24_2','elevation24_3','elevation24_4']


# In[4]:


fields_to_be_added = []
for new_field_name in new_field_names:
    print(new_field_name)
    new_field = {
    "name": new_field_name,
    "type": "esriFieldTypeDouble",
    "alias": new_field_name,
    #"length": 20,
    "nullable": True,
    "editable": True,
    "visible": True,
    "domain": None
    }
    track_flayer.manager.add_to_definition({'fields':[new_field]})


# In[ ]:




