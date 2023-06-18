#%%
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import pandas as pd
#%%
gis = GIS("https://arcportal-ucop-corps.usace.army.mil/s0portal")

#%%
layer = FeatureLayer("https://arcportal-ucop-corps.usace.army.mil/s0arcgis/rest/services/Hosted/Climate_and_Economic_Justice_Screening_Data/FeatureServer/0")
fields = layer.properties['fields']

#%%
field_to_update = {}

#%% 
dictionary_file = r"C:\Users\M3ECHJJJ\Downloads\columns.csv"
#%% create a dictionary of column 1 and column 2 from the csv file
df = pd.read_csv(dictionary_file)
df.set_index('shapefile_column', inplace=True)
alias_key =df.to_dict()

#%%
for field in fields:
    try:
        print(field['name'])
        field_to_update[field['name']]= alias_key[field['name'].upper()]
    except Exception as e:
        pass


#%%
field_to_update

#%%
alias_key['SF']



# %%
layer.manager.update_definition({'fields': {'name': key, 'alias': value}})
#%%
column_name[0]
# %%
alias_key = alias_key['column_name']
# %%

for key, value in alias_key.items():
    layer.manager.update_definition({'fields': {'name': key, 'alias': value}})


# %%
updates_to_push
# %%
