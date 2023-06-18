#%%
print('Importing Modules')
from arcgis import GIS
import time, os
import smtplib, requests
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate



#%% Connect to your GIS
print('Connecting to NWD Portal')
gis = GIS('https://geoportal.nwd.usace.army.mil/g0portal')
layer_item = gis.content.get('9f1f8b10f836435599b25ab56ef59a48')
layers = layer_item.layers
flayer = layers[0]
oid_list = []
#%%
print('Querying for records to email')
df = layers[0].query(where="emailed is null").sdf
print('Located {} records to email'.format(len(df)))
#%%
for index, row in df.iterrows():
    print(f"Emailing {index+1} of {len(df)}")

    emailstring = f'''<p>TASK NAME: {row['task_name']}</p>

<p>PROJECT NAME: {row['project_name']}</p>

<p>PROGRAM NAME: {row['program_name']}</p>

<p>PRIORITY: {row['task_priority']}</p>

<p>LABOR CODE: {row['labor_code']}</p>

<p>ASSIGNED BY: {row['assigned_by']} {row['emailcalc']}</p>

<p>RESPONSIBLE EMPLOYEE: {row['responsible_employee']}</p>

<p>DESCRIPTION: {row['description']}</p>

<p><a href="https://geoportal.nwd.usace.army.mil/g0portal/apps/dashboards/9c513c0cb2bf4363b9192f14d452abaa">VIEW OR MANAGE THE REQUEST</a></p>

    '''
    host = 'SMTP.USACE.ARMY.MIL'
    port = 25
    sender = 'no-reply@usace.army.mil'
    to = 'TR GIS Team'
    msg = MIMEMultipart()
    msg['From'] = 'TR Cadastral Requests <no-reply@usace.army.mil>'
    msg['To'] = to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = 'New Cadastral Request- ' + row['task_name']
    msg.attach(MIMEText(emailstring, "html"))
    smtp = smtplib.SMTP(host, port)
    smtp.sendmail(sender, ['jason.j.jordan@usace.army.mil','Michael.S.Cabrera@usace.army.mil','gregory.mireles@usace.army.mil','shawna.m.westhoff@usace.army.mil'], msg.as_string())
    smtp.close()
    oid_list.append(row['objectid'])
# %%

if len(oid_list) > 0:
    updates_to_push = []
    for o in oid_list:
        updates_to_push.append({'attributes':{'objectid':o,'emailed':'Yes'}})
    update_result = flayer.edit_features(updates=updates_to_push)

# %%
