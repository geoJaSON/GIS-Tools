import pandas as pd
from arcgis import GIS
import numpy as np

m_map = {'M0':'SWD','M2':'SWF','M3':'SWG','M4':'SWL','M5':'SWT'}

def clean_p2_number(x):
    if '-' not in x['cw_project']:
        x['p2_number'] = '000000'
        return x
    else:
        x['p2_number'] = str(x['cw_project'].split(" - ")[0].split(" ")[-1])
        x['cw_project'] = x['cw_project'].split(" - ")[1]
        return x


#%% Prep swd2101.xlsx

swd2101 = pd.read_excel(r"database\P2Support\SWTDB\SWD 2101\SWD2101.xlsx")
swd2101.columns = swd2101.columns.str.replace(r'[^0-9a-zA-Z:,]+', '_',regex=True) #Replace header special characters with '_'
swd2101.columns = swd2101.columns.str.lower() #Convert header to lower case for postgresql
swd2101['p2_number'] = ''   #Create column for P2 number
swd2101 = swd2101.apply(clean_p2_number, axis=1)  #parse out P2 number into seperate column and isolate name
swd2101 = swd2101.replace({np.nan: None}) #Convert NaN to NONE
swd2101['district'] = swd2101['eroc'].apply(lambda s :s[s.find("(")+1:s.find(")")]) #Parse out district symbols
swd2101['division'] = swd2101['district'].apply(lambda d : d[:2]+'D') #get division from district
p2_numbers = list(swd2101['p2_number'].unique()) #Make a list of unique P2 numbers
#swd2101 = swd2101.set_index(['p2_number','account'])

#%% Prep DB_Milestone.csv

db_milestones = pd.read_csv(r"database\P2Support\SWTDB\SWD 2101\DB_MILESTONES.csv")
db_milestones.columns = db_milestones.columns.str.replace(r'[^0-9a-zA-Z:,]+', '_',regex=True) #Replace header special characters with '_'
db_milestones.columns = db_milestones.columns.str.lower() #Convert header to lower case for postgresql
db_milestones['proj_subtype_name'] = db_milestones['proj_subtype_name'].str.replace('and', '&') #Clean up type field
db_milestones = db_milestones.rename({'project_number':'p2_number'}, axis=1) #rename field to match others
db_milestones['district'] = db_milestones['foa_code'].apply(lambda x :m_map[x]) #convert m numbers to symbols
db_milestones['division'] = db_milestones['district'].apply(lambda d : d[:2]+'D') #get division from district
db_milestones = db_milestones.replace({np.nan: None})   #Convert NaN to NONE
#db_milestones= db_milestones.set_index(['p2_number', 'short_name'])

#Convert all dates to millisecond integer for push to feature layer
db_milestones['current_schedule'] = pd.to_datetime(db_milestones['current_schedule']).astype(np.int64)/1e6
db_milestones['bl_date_created'] = pd.to_datetime(db_milestones['bl_date_created']).astype(np.int64)/1e6
db_milestones['task_refresh_date'] = pd.to_datetime(db_milestones['task_refresh_date']).astype(np.int64)/1e6
db_milestones['actual_date'] = pd.to_datetime(db_milestones['actual_date']).astype(np.int64)/1e6
db_milestones['bl_schedule'] = pd.to_datetime(db_milestones['bl_schedule']).astype(np.int64)/1e6
db_milestones['bl_actual'] = pd.to_datetime(db_milestones['bl_actual']).astype(np.int64)/1e6
db_milestones['refresh_date'] = pd.to_datetime(db_milestones['refresh_date']).astype(np.int64)/1e6
db_milestones['rymd_date'] = pd.to_datetime(db_milestones['rymd_date'], format='%Y%m%d')
db_milestones['rymd_date'] = pd.to_datetime(db_milestones['rymd_date']).astype(np.int64)/1e6

#%% Connect to GIS

tokens = pd.read_csv(r"C:\Users\M3ECHJJJ\Documents\Tokens.csv", index_col='Site')
gis = GIS(tokens.at['uCOP','URL'])
layer_item = gis.content.get('a8b957e2ffa9480fbcd8d9ee123a94a4')
layers = layer_item.layers
flayer = layers[0]
fset = flayer.query()
tables = layer_item.tables
funding_flayer = tables[1]
milestone_flayer = tables[0]

#%% Grab objectIDs and globalIDs to map updates and relationships

sdf = pd.DataFrame.spatial.from_layer(flayer)
p2_keys = {row['p2number']: row['globalid'] for value, row in sdf.iterrows()}
funding_sdf =pd.DataFrame.spatial.from_layer(funding_flayer)
funding_keys = {str(row['p2_number'])+row['account']: row['objectid'] for value, row in funding_sdf.iterrows()}
milestone_sdf =pd.DataFrame.spatial.from_layer(milestone_flayer)
milestone_keys = {str(row['p2_number'])+row['task_name_and_code']: row['objectid'] for value, row in milestone_sdf.iterrows()}


#%% Update Funding Accounts

def assemble_funding_updates(row):
    try: #If record is found, create an update object
        edit_feature = {'objectid': funding_keys[str(row['p2_number'])+row['account']]} #Get objectID to update
        for col in swd2101.columns: #Map DF columns to FS columns and insert row values
            edit_feature[col] = row[col]
        feat = {'attributes': edit_feature} #Finalize the update object
        updates_to_push.append(feat) #append object into list
    except KeyError: #If not found, create an insert object
        print(str(row['p2_number'])+row['account'])
        try:
            add_feature = {'parentglobalid':p2_keys[str(row['p2_number'])]}
        except:
            add_feature = {}

        for col in swd2101.columns: #Map DF columns to FS columns and insert row values
            add_feature[col] = row[col]
        feat = {'attributes': add_feature} #append object into list
        adds_to_push.append(feat) #append object into list

updates_to_push = [] #Create list of all update objects to push
adds_to_push = [] #Create list of all insert objects to push
swd2101.apply(lambda row: assemble_funding_updates(row), axis=1) #apply the assumble updates function to DF
update_result = funding_flayer.edit_features(updates=updates_to_push, adds=adds_to_push, rollback_on_failure=False) #Commit the update and insert lists

#%% Update Milestones

def assemble_milestone_updates(row):
    try:
        edit_feature = {'objectid': milestone_keys[str(row['p2_number'])+row['task_name_and_code']]}
        for col in db_milestones.columns:
            edit_feature[col.lower()] = row[col]
        feat = {'attributes': edit_feature}
        updates_to_push.append(feat)
    except KeyError:
        print(str(row['p2_number'])+row['task_name_and_code'])
        try:
            add_feature = {'parentglobalid':p2_keys[str(row['p2_number'])]}
        except:
            add_feature = {}

        for col in db_milestones.columns:
            add_feature[col.lower()] = row[col]
        feat = {'attributes': add_feature}
        adds_to_push.append(feat)

updates_to_push = []
adds_to_push = []
db_milestones.apply(lambda row: assemble_milestone_updates(row), axis=1)
update_result = milestone_flayer.edit_features(updates=updates_to_push, adds=adds_to_push, rollback_on_failure=False)

len(updates_to_push)
len(adds_to_push)
update_result = funding_flayer.edit_features(adds=adds_to_push, rollback_on_failure=False) #Commit the update and insert lists
