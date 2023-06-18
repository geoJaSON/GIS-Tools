import pandas as pd
from arcgis import GIS
pd.set_option('display.max_rows', None)
pd.options.display.float_format = '{:,.2f}'.format
df = pd.read_excel(r"D:\Copy of 23 Mar 2022 - SPK Projects Financial Report.xlsx",1)
df['project']=df.columns[0]
df.rename(columns={ df.columns[0]: "Subproject" }, inplace = True)
df1 = df.groupby(['Sum of AUTHORIZED', 'Sum of OBLIGATIONS','Sum of COMMITMENTS','Sum of AVAILABLE']).last()
df1['p2_number']=df1['project'].str.split(' ')
df1['p2_number'] = df1['p2_number'].str[0]
df1.reset_index(inplace=True)

df.columns = df.iloc[0]
df


tokens = pd.read_csv(r"C:\Users\M3ECHJJJ\Documents\Tokens.csv", index_col='Site')
gis = GIS(tokens.at['uCOP','URL'])
prb_layer_item = gis.content.get('999b0fc4c1444e7eaf66a0e25e5f525d')

funding_layers = prb_layer_item.tables
funding_fset=funding_layers[0].query()
funding_features = funding_fset.features
funding_flayer = funding_layers[0]

def assemble_updates(row):
    try:
        add_feature = {'subproject': row['Subproject']}
        add_feature['sum_of_available'] = row['Sum of AVAILABLE']
        add_feature['sum_of_commitments'] = row['Sum of COMMITMENTS']
        add_feature['sum_of_obligations'] = row['Sum of OBLIGATIONS']
        add_feature['sum_of_authorized'] = row['Sum of AUTHORIZED']
        add_feature['project_name'] = row['project']
        add_feature['p2_number'] = row['p2_number']
        feat = {'attributes': add_feature}
        adds_to_push.append(feat)
    except Exception as e:
        print(e)
# %%

updates_to_push = []
adds_to_push = []
df1.apply(lambda row: assemble_updates(row), axis=1)
print('Total:', len(df1), 'Updates:', len(updates_to_push), 'Adds:', len(adds_to_push))
update_result = funding_flayer.edit_features(updates=updates_to_push, adds=adds_to_push, rollback_on_failure=False)
