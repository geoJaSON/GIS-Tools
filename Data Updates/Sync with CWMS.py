#!/usr/bin/env python
# coding: utf-8

# In[1]:


from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import numpy as np
import tqdm as tqdm


# In[2]:


cwms_url = 'https://geoportal-dmzu.usace.army.mil/s1arcgis/rest/services/ERDC/cwms/FeatureServer/1'
cwms = FeatureLayer(cwms_url)
cwms_swd = cwms.query(where="db_office_id IN ('SWG', 'SWF', 'SWL', 'SWT')")
cwms_df = cwms_swd.sdf
cwms_df = cwms_df.fillna(0)


# In[3]:


swd_url = 'https://arcservices-ucop-corps.usace.army.mil/s0arcgis/rest/services/Hosted/CWMS_Geoevent/FeatureServer/0'
swd_flayer = FeatureLayer(swd_url)
swd_fset = swd_flayer.query()
swd_features=swd_fset.features


# In[4]:


columns_to_update = ['cur_stor','pct_flood_full','cur_elev','elev_date','cur_stage','cur_outflow','outflow_date','cur_inflow','inflow_date','cur_flood_stor','stor_flood_date','cur_drought_stor','stor_drought_date','pct_conservation_full','pct_full','elev_24hr_change','stage_24hr_change','tw_elev_24hr_change','cur_outflow_daily_avg','tw_stage_24hr_change','cur_outflow_daily_avg_date','cur_sur_area']


# In[ ]:


for index, row in cwms_df.iterrows():
    try:
        t_feature = [f for f in swd_features if f.attributes['location_id']==row['LOCATION_ID']][0]
        attributes_dict = {'objectid':t_feature.attributes['objectid']}
        for col in columns_to_update:
            attributes_dict[col]=row[col.upper()]
        if row['PCT_FLOOD_FULL'] > 0 and row['PCT_FLOOD_FULL'] <100:
            attributes_dict['hexcolor'] = 'FFFF00'
        elif row['PCT_FLOOD_FULL'] > 100:
            attributes_dict['hexcolor'] = 'FF0000'
        else:
            attributes_dict['hexcolor'] = 'ffffff'
        edit_feature = {"attributes": attributes_dict} 
        update_result = swd_flayer.edit_features(updates=[edit_feature])
        if update_result['updateResults'][0]['success'] == True:
            pass
        else:
            print(row['LOCATION_ID'],update_result['updateResults'][0]['error'])
    except Exception as e:
        print('Nope',e)


# In[9]:


update_result


# In[11]:


cwms_df


# In[ ]:




