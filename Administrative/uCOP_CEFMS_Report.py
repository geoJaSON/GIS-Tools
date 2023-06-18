#%%
tinput = input('Enter the date of the report (mm/dd/yyyy): ')
rinput = input('Amount committed to REDi: ')
#%%
import pandas as pd
import numpy as np
import time

#%% convert '11/12/2022' to unix time
def convert_date_to_unix(date):
    return int(time.mktime(time.strptime(date, '%m/%d/%Y')))*1000
tinput = convert_date_to_unix(tinput)

#%%
file = r"C:\Users\M3ECHJJJ\Downloads\Nov 28 uCOP 8846h1 work item detail.xlsx"
paxlist  = {'wilson':'Wilson and Garo','jordan':'Jason Jordan','vicars':'Julie Vicars', 'schultz':'Michelle Schultz','adams':'Beth Adams','holland':'Jennifer Holland','cox':'Christy Cox','vera':'Rick Vera','lundstrum':'Russel Lundstrum','kist':'Jennifer Kist'}


#%%
df = pd.read_csv(r"C:\Users\M3ECHJJJ\Downloads\uCOP 30 JAN fwi_det_ss_857.csv")
paxlist  = {'ayanian':'Garo Ayanian','duke':'Matt Duke','wilson':'Wilson and Garo','hessler':'Doug Hessler','jordan':'Jason Jordan','vicars':'Julie Vicars', 'schultz':'Michelle Schultz','adams':'Beth Adams','holland':'Jennifer Holland','cox':'Christy Cox','vera':'Rick Vera','lundstrum':'Russel Lundstrum','kist':'Jennifer Kist'}
df.columns = ['Work Item', 'Work Item Desc', 'PRAC No', 'PRAC Line No', 'OBLI No', 'DO No', 'MOA', 'EOR', 'Description', 'Org Code', 'Org Name', 'Labor Code', 'Resource','Obligation Amt','Cumulative Expenditures','Undelivered Orders','Commitments']

#%%
for index, row in df.iterrows():
    if 'travel' in row['Description'].lower():
        df.loc[index, 'Resource'] = 'Travel'
    # if any of paxlist keys in in row['Description'], then assign the value to new column
    for key in paxlist:
        if key in row['Description'].lower():
            df.loc[index, 'Name'] = paxlist[key]
            break

df['Description'] = df['Description'].str.title()
df['Resource Code'] = df['Resource'].str.title()
df = df.astype(object).replace(np.nan, 'None')

# %%
from arcgis.gis import GIS
gis = GIS('https://arcportal-ucop-corps.usace.army.mil/s0portal')
layer_item = gis.content.get('f88fc60f368740e592ab49b756844ba6')

layers = layer_item.layers
fset=layers[0].query()
features = fset.features
flayer = layers[0]
# %%

adds_to_push = [{'attirubtes': {'description': 'REDi Upkeep','commitments':600000,'obligation_amount':930000}}]

def assemble_updates(row):
        add_feature = {'prc_ob': row['Work Item']}
        add_feature['line_item'] = row['PRAC No']
        add_feature['moa'] = row['MOA']
        add_feature['eor'] = row['EOR']
        add_feature['description'] = row['Description']
        add_feature['org_code'] = row['Org Code']
        add_feature['org_name'] = row['Org Name']
        add_feature['resource'] = row['Resource']
        add_feature['obligation_amount'] = row['Obligation Amt']
        add_feature['cumulative_exp'] = row['Cumulative Expenditures']
        add_feature['undelivered_orders'] = row['Undelivered Orders']
        add_feature['commitments'] = row['Commitments']
        add_feature['pname'] = row['Name']
        add_feature['current_report'] = 'yes'
        add_feature['report_date'] = tinput
        feat = {'attributes': add_feature}
        adds_to_push.append(feat)
        
df.apply(lambda row: assemble_updates(row), axis=1)
#%%
flayer.calculate(where='objectid > 0', calc_expression={"field":'current_report',"value" :'no'})
update_result = flayer.edit_features(adds=adds_to_push, rollback_on_failure=False)


#%%
import pytz
# %%
