
# %%

print("Loading Modules...")
from datetime import datetime, timedelta
from arcgis.gis import GIS
import pandas as pd
import numpy as np
import xlwt
from xlwt import Workbook
import os

last_day = (datetime.datetime.today().replace(day=1) - timedelta(days=1))
start_day = (datetime.datetime.today().replace(day=1) - timedelta(days=last_day.day))


# %%
tokens = pd.read_csv(r"C:\Users\M3ECHJJJ\Documents\Tokens.csv", index_col='Site')

portals = {'SWD-EM': [tokens.at['SWD-EM','Username'], tokens.at['USACE-SWG','Password']],
           'USACE-SWG': [tokens.at['CESWG','Username'], tokens.at['USACE-SWG','Password']], 'CESWG': [tokens.at['USACE-SWG','Username'], tokens.at['USACE-SWG','Password']]}


# %%


query_df = pd.DataFrame(
    columns=['Entitlement', 'Total', 'Assigned', 'Remaining', 'AGOL'])
cred_df = pd.DataFrame()


# %%


for key, value in portals.items():
    try:
        print('Signing into', key)
        gis = GIS(username=value[0], password=value[1])
        print('    Getting license data')
        for i in gis.admin.license.all():
            try:
                print('       ', i)
                t_df = i.report
                t_df['AGOL'] = key
                query_df = query_df.append(t_df)
            except:
                pass
        print('    Getting user count')
        query_df = query_df.append({'AGOL': key, 'Entitlement': 'Creators', 'Assigned': len(
            [acc for acc in gis.users.search(max_users=500) if acc.level == "2"])}, ignore_index=True)
        # query_df = query_df.append({'AGOL':key,'Entitlement':'CreditsTotal','Assigned':0},ignore_index=True)
        print('    Pulling credit usage')
        cred = gis.admin.credits.credit_usage(
            start_time=last_day, end_time=start_day)
        cred['AGOL'] = key
        cred_df = cred_df.append(cred, ignore_index=True)
    except Exception as e:
        print(e)
print("Gathering Stats...")
query_df['Entitlement'] = query_df['Entitlement'].str.rstrip('N')
portals_df = query_df.pivot_table(
    index="AGOL", columns="Entitlement", values="Assigned", aggfunc=np.sum)
portals_df = portals_df.fillna(0)
cred_df = cred_df.fillna(0)
cred_df = cred_df.loc[:, (cred_df != 0).any(axis=0)]
cred_df = cred_df.set_index('AGOL')
portals_df = pd.concat([cred_df, portals_df], axis=1)


# %%


print('Writing results to XLS')
wb = Workbook()
xlwt.add_palette_colour("custom_gray", 0x21)
wb.set_colour_RGB(0x21, 251, 228, 228)
xlwt.add_palette_colour("custom_tan", 0x22)
wb.set_colour_RGB(0x22, 204, 255, 153)
for index, row in portals_df.iterrows():
    a_count = row['notebooks'] + row['schdnotebks']
    s_count = row['features'] + row['scene'] + \
        row['tiles'] + row['vectortiles'] + row['portal']
    total_count = a_count + s_count

    sheet = wb.add_sheet(index)
    boldstyle = xlwt.easyxf('font: bold 1')
    boldcenter = xlwt.easyxf(
        'font: bold 1;align: wrap on, vert center, horiz center')
    boldcentergray = xlwt.easyxf(
        'font: bold 1;align: wrap on, vert center, horiz center;pattern: pattern solid, fore_colour custom_gray')
    inputtan = xlwt.easyxf(
        'align: wrap on, vert center, horiz center;pattern: pattern solid, fore_colour custom_tan')
    # row,column
    sheet.write(0, 0, 'Report Date', boldstyle)
    sheet.write(0, 1, 'From:', boldstyle)
    sheet.write(0, 2, start_day.strftime("%m/%d/%Y"), inputtan)
    sheet.write(0, 3, 'To:', boldstyle)
    sheet.write(0, 4, last_day.strftime("%m/%d/%Y"), inputtan)
    sheet.write(2, 0, 'USACE-SWG')
    sheet.write(2, 1, 'Rick Vera')
    sheet.write(1, 0, 'Office Name', boldstyle)
    sheet.write(1, 1, 'POC/Administrator', boldstyle)

    sheet.write(1, 4, 'Members', boldcentergray)
    sheet.write_merge(1, 1, 5, 9, 'Credits Consumed', boldcentergray)
    sheet.write(2, 4, 'Creator Count', boldstyle)
    sheet.write(3, 4, str(int(row['Creators'])), inputtan)
    sheet.write(2, 5, 'Credits Total:', boldstyle)
    sheet.write(3, 5, str(int(total_count)), inputtan)
    sheet.write(2, 6, 'Storage:', boldstyle)
    sheet.write(3, 6, str(int(s_count)), inputtan)
    sheet.write(2, 7, 'Analytics:', boldstyle)
    sheet.write(3, 7, str(int(a_count)), inputtan)
    sheet.write(2, 8, 'Subscriber:', boldstyle)
    sheet.write(3, 8, "0", inputtan)
    sheet.write(2, 9, 'Published:', boldstyle)
    sheet.write(3, 9, "0", inputtan)

    sheet.write_merge(4, 4, 0, 2, 'Core Product Counts', boldcentergray)
    sheet.write(5, 0, 'Pro Desktop Advanced', boldcenter)
    sheet.write(6, 0, str(int(row['desktopAdv'])), inputtan)
    sheet.write(5, 1, 'Pro Desktop Basic', boldcenter)
    sheet.write(6, 1, str(int(row['desktopBasic'])), inputtan)
    sheet.write(5, 2, 'Pro Desktop Standard', boldcenter)
    sheet.write(6, 2, str(int(row['desktopStd'])), inputtan)

    sheet.write_merge(8, 8, 0, 11, 'Extension Counts:', boldcentergray)
    sheet.write(9, 0, 'Pro 3D Analyst', boldcenter)
    sheet.write(10, 0, str(int(row['3DAnalyst'])), inputtan)

    sheet.write(9, 1, 'Pro Aviation Airports', boldcenter)
    sheet.write(10, 1, str(int(row['airports'])), inputtan)

    sheet.write(9, 2, 'Pro Data Reviewer', boldcenter)
    sheet.write(10, 2, str(int(row['dataReviewer'])), inputtan)

    sheet.write(9, 3, 'Pro Defense Mapping', boldcenter)
    sheet.write(10, 3, str(int(row['defense'])), inputtan)

    sheet.write(9, 4, 'Pro Geostatistical Analyst', boldcenter)
    sheet.write(10, 4, str(int(row['geostatAnalyst'])), inputtan)

    sheet.write(9, 5, 'Pro Maritime Charting', boldcenter)
    sheet.write(10, 5, str(int(row['maritime'])), inputtan)

    sheet.write(9, 6, 'Pro Image Analyst', boldcenter)
    sheet.write(10, 6, "0", inputtan)

    sheet.write(9, 7, 'Pro Network Analyst', boldcenter)
    sheet.write(10, 7, str(int(row['networkAnalyst'])), inputtan)

    sheet.write(9, 8, 'Pro Production Mapping', boldcenter)
    sheet.write(10, 8, str(int(row['productionMap'])), inputtan)

    sheet.write(9, 9, 'Pro Publisher', boldcenter)
    sheet.write(10, 9, str(int(row['publisher'])), inputtan)

    sheet.write(9, 10, 'Pro Spatial Analyst', boldcenter)
    sheet.write(10, 10, str(int(row['spatialAnalyst'])), inputtan)

    sheet.write(9, 11, 'Pro Workflow Manager', boldcenter)
    sheet.write(10, 11, str(int(row['workflowMgr'])), inputtan)

    sheet.write_merge(12, 12, 0, 7, 'Add-On Products:', boldcentergray)

    sheet.write(13, 0, 'Insights', boldcenter)
    try:
        sheet.write(14, 0, str(int(row['insights'])), inputtan)
    except:
        sheet.write(14, 0, "0", inputtan)

    sheet.write(13, 1, 'Business Analyst Online', boldcenter)
    try:
        sheet.write(14, 1, str(int(row['BusinessAnlyst'])), inputtan)
    except:
        sheet.write(14, 1, "0", inputtan)

    sheet.write(13, 2, 'Navigator', boldcenter)
    try:
        sheet.write(14, 2, str(int(row['workflowMgr'])), inputtan)
    except:
        sheet.write(14, 2, "0", inputtan)

    sheet.write(13, 3, 'Tracker', boldcenter)
    try:
        sheet.write(14, 3, str(int(row['workflowMgr'])), inputtan)
    except:
        sheet.write(14, 3, "0", inputtan)

    sheet.write(13, 4, 'Community Analyst', boldcenter)
    try:
        sheet.write(14, 4, str(int(row['CommunityAnlyst'])), inputtan)
    except:
        sheet.write(14, 4, "0", inputtan)

    sheet.write(13, 5, 'Drone2Map', boldcenter)
    try:
        sheet.write(14, 5, str(int(row['workflowMgr'])), inputtan)
    except:
        sheet.write(14, 5, "0", inputtan)

    sheet.write(13, 6, 'ArcGIS Maps for Power BI', boldcenter)
    try:
        sheet.write(14, 6, str(int(row['workflowMgr'])), inputtan)
    except:
        sheet.write(14, 6, "0", inputtan)

    sheet.write(13, 7, 'App Studio Standard', boldcenter)
    try:
        sheet.write(14, 7, str(int(row['appstudiostd'])), inputtan)
    except:
        sheet.write(14, 7, "0", inputtan)

    sheet.col(0).width = 4000
    sheet.col(1).width = 4000
    sheet.col(2).width = 4000
    sheet.col(3).width = 4000
    sheet.col(4).width = 4000
    sheet.col(5).width = 4000
    sheet.col(6).width = 4000
    sheet.col(7).width = 4000
    sheet.col(8).width = 4000
    sheet.col(9).width = 4000
    sheet.col(10).width = 4000
    sheet.col(11).width = 4000
    sheet.col(12).width = 4000


# %%
filename = "AGOL_Report_"+last_day.strftime("%b_%Y")+'.xls'
wb.save(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop',filename))
print("Results written to",os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop',filename))

# %%
