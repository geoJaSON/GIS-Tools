#Using PDFminer3
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import PDFPageAggregator
from pdfminer3.converter import TextConverter
import io, re, os, datetime, pandas as pd, geopy, geopy.distance, requests, json, numpy as np, math, difflib
from arcgis import GIS
from arcgis.features import SpatialDataFrame, Feature, FeatureSet
from arcgis import geometry

#%% Get URL of PDF to Parse

url = "https://navcen.uscg.gov/?pageName=lnmDistrict&region=8&ext=g"
webpage = requests.get(url)

for l in webpage:
    if '<strong>New!</strong>' in str(l):
        path = 'https://navcen.uscg.gov/pdf/lnms/'+re.findall('lnm\d\d\d\dg202\d.pdf', str(l))[0]

#%% Download PDF file in chuncks due to size

r = requests.get(path, stream = True)
with open('lnm.pdf',"wb") as pdf:
    for chunk in r.iter_content(chunk_size=1024):
           if chunk:
             pdf.write(chunk)

#%% Get Text from PDF and delete file afterward

resource_manager = PDFResourceManager()
fake_file_handle = io.StringIO()
converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
page_interpreter = PDFPageInterpreter(resource_manager, converter)

with open('lnm.pdf', 'rb') as fh:

    for page in PDFPage.get_pages(fh,
                                  caching=True,
                                  check_extractable=True):
        page_interpreter.process_page(page)

    text = fake_file_handle.getvalue()

converter.close()
fake_file_handle.close()
os.remove('lnm.pdf')

#%% Load mile_markers_list and relative locations Data

giww_df = pd.read_csv('https://raw.githubusercontent.com/geoJaSON/Open-GIS-Processes/main/giww_markers.csv')
giww_df = giww_df.set_index('MILE')
relative_lookup = pd.read_csv(r'C:\Users\M3ECHJJJ\github\GIS_Tasks\relative_lookup.csv')
rl = relative_lookup['CITY_NM'].tolist()
navaid_df = pd.read_csv(r"C:\Users\M3ECHJJJ\github\GIS_Tasks\navaids.csv")
navaid_df = navaid_df.set_index('LLNR')
bridge_df = pd.DataFrame({'bridge':['1495','KCS Railroad'], 'POINT_X':[-95.343683,-94.091537],'POINT_Y':[28.951252,30.081850]})

def get_nav(number):
    x = navaid_df.at[int(number),'POINT_X']
    y = navaid_df.at[int(number),'POINT_Y']
    return [x,y]

def get_bridge(loc):
    x = bridge_df.loc[bridge_df['bridge'] == str(loc), 'POINT_X'].iloc[0]
    y = bridge_df.loc[bridge_df['bridge'] == str(loc), 'POINT_Y'].iloc[0]
    return [x,y]

def get_mm(marker):
    dir = giww_df.at[int(marker),'azimuth']
    start = geopy.Point(giww_df.at[int(marker),'startlat'], giww_df.at[int(marker),'startlong'])
    d = geopy.distance.distance(miles=marker-(int(marker)))
    p = d.destination(point=start, bearing=giww_df.at[int(marker),'azimuth'])
    return [p.longitude, p.latitude]

def sort_box(t):
    s=sorted(t , key=lambda k: [k[1], k[0]])
    try:
        s[3],s[2]=s[2],s[3]
    except:
        pass
    return s

def group_coordinates(t):
    c_list = sort_box(t)
    if len(t) ==5:
        c_list = []
        c_list.append(t[0])
        c_list.append(sort_box(t[1:5]))
    if len(t) ==9:
        c_list = []
        c_list.append(t[0])
        c_list.append(sort_box(t[1:5]))
        c_list.append(sort_box(t[5:9]))
    if len(t) ==13:
        c_list = []
        c_list.append(t[0])
        c_list.append(sort_box(t[1:5]))
        c_list.append(sort_box(t[5:9]))
        c_list.append(sort_box(t[9:14]))
    return c_list

#%% Filter text to only TX notices

text = text.split('SECTION VII - GENERAL')[1]
text = text.split('SECTION VIII - LIGHT LIST CORRECTIONS')[0]
text = text.split('TX - ')[1:]

#%% Set regex expressions to find mile markers, dates, and coordinates

point_reg = '[0-9][0-9]-[0-9][0-9]-[0-9][0-9].[0-9]*N [0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].[0-9]*W'
date_reg = '(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{1,2})\,\s+(\d{4})'
mile_reg = 'Mile [0-9]{1,3}.[0-9]'
navaid_reg = 'LLNR-\d\d\d\d\d'
relative_reg = '(west of |east of |south of |north of)(.*?)(?=,| and)'
bridge_reg = 'Road (\d+)'

#%% Extract Data from text and place into DF

df = pd.DataFrame(columns = ['area','subarea','lnm','geolocation_type','coordinates_list','mile_markers_list','dates_list','max_date','summary','derived_geometry','notice_type','SHAPE'])

for notice in text:
    notice=notice.replace('\n\n','<br>')
    notice=notice.replace('\n','<br>')
    notice=notice.replace(' - <br>',' - ')
    row = {}
    parts = notice.split(' - ')
    if len(parts)==2:
        row['area']=parts[0]
    else:
        row['area']=parts[0]
        row['subarea']=parts[1].replace('Public Notice','')
    row['summary']=''.join(parts[-1].split('<br>')[1:-3])
    row['notice_type']=parts[-1].split('<br>')[0]
    dates = re.findall(date_reg, notice)
    dates = [' '.join(tup) for tup in dates]
    dates_list = [datetime.datetime.strptime(date, '%B %d %Y').date() for date in dates]
    try:
        row['max_date']= max(dates_list)
    except:
        pass
    row['dates_list']=dates
    row['lnm']=notice.split('<br>')[-2]
    coordinates = re.findall(point_reg, notice.replace('<br>',''))
    milemarkers = re.findall(mile_reg, notice.replace('<br>',''))
    relatives = re.findall(relative_reg, notice.replace('<br>',''))
    bridges = []
    #if any(ext in notice for ext in bridge_df['bridge'].tolist()):
    for loc in bridge_df['bridge'].tolist():
        if loc in notice:
            bridges.append(loc)
    navaids = re.findall(navaid_reg, notice.replace('<br>',''))
    row['coordinates_list']=coordinates
    if len(coordinates) >0:
        row['geolocation_type']='Coordinate Provided'
    elif 'GIWW' in notice and len(milemarkers) >0:
        row['geolocation_type']='GIWW Mile Markers'
        row['mile_markers_list']=milemarkers
    elif len(milemarkers) >0 and 'bridge' not in notice.lower():
        row['geolocation_type']='Mile Markers'
        row['mile_markers_list']=milemarkers
    elif len(navaids) >0:
        row['geolocation_type']='NAVAIDs'
        row['mile_markers_list']=navaids
    elif len(bridges) >0:
        row['geolocation_type']='Bridge'
        row['mile_markers_list']=bridges
    elif len(relatives) >0:
        row['mile_markers_list']=relatives
        row['geolocation_type']='Relative'
    else:
        row['geolocation_type']='Geocode'
    df = df.append(row, ignore_index=True)

df = df.replace({np.nan: None})
df['max_date'] = pd.to_datetime(df['max_date']).astype(np.int64)/1e6

#%% Calculate relative locations

for index, row in df.iterrows():
    if (row['geolocation_type'])=="Relative":
        relatives = row['mile_markers_list']
        for i in relatives:
            if any(x in i[0] for x in ['east','west']):
                x_holder = difflib.get_close_matches(i[1], rl, n=1)
                if len(x_holder) >0:
                    x = relative_lookup.loc[relative_lookup['CITY_NM'] == x_holder[0], 'POINT_Y'].iloc[0]
            if any(x in i[0] for x in ['north','south']):
                y_holder = difflib.get_close_matches(i[1], rl, n=1)
                if len(y_holder) >0:
                    y = relative_lookup.loc[relative_lookup['CITY_NM'] == y_holder[0], 'POINT_X'].iloc[0]
        df.at[index,'coordinates_list'] = [[y,x]]

#%% Get locations of found bridges

for index, row in df.iterrows():
    c_list = []
    if row['geolocation_type'] =='Bridge':
        point_list = row['mile_markers_list']
        for i in point_list:
            c_list.append(get_bridge(i))
        df.at[index,'coordinates_list'] = c_list

#%% Get GIWW mile_markers_list coordinates_list

for index, row in df.iterrows():
    c_list = []
    if row['geolocation_type'] =='GIWW Mile Markers':
        point_list = row['mile_markers_list']
        for i in point_list:
            c_list.append(get_mm(int(float(i.split(' ')[-1]))))
        df.at[index,'coordinates_list'] = c_list

#%% Get coordinates of Navaids

for index, row in df.iterrows():
    c_list = []
    if row['geolocation_type'] =='NAVAIDs':
        point_list = row['mile_markers_list']
        for i in point_list:
            c_list.append(get_nav(i.split('-')[1]))
        df.at[index,'coordinates_list'] = c_list



#%% Convert DMS to DD

for index, row in df.iterrows():
    c_list = []
    if row['geolocation_type'] =='Coordinate Provided':
        for i in row['coordinates_list']:
            deg, minutes, seconds =  i.replace('N','').replace('W','').split(' ')[0].split('-')
            nlat = float(deg) + float(minutes)/60 + float(seconds)/(60*60)
            deg, minutes, seconds =  i.replace('N','').replace('W','').split(' ')[1].split('-')
            nlong = float(deg) + float(minutes)/60 + float(seconds)/(60*60)
            if nlong > 0:
                nlong = nlong*(-1)
            c_list.append([nlong,nlat])
        df.at[index,'coordinates_list'] = group_coordinates(c_list)

#%% Geocode leftovers

def geocode(addressLine):
    try:
        addressLine = addressLine.replace(' ','%20')
        resp = requests.get(url=r'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?Address=' + addressLine + '&outFields=*&forStorage=false&f=pjson')
        data = resp.json()
        y = data['candidates'][0].get("location",{}).get("y")
        x = data['candidates'][0].get("location",{}).get("x")
        return x, y
    except:
        return 0,0

for index, row in df.iterrows():
    if len(row['coordinates_list']) == 0:
        if row['subarea'] != None:
            long, lat = geocode(row['subarea'])
            df.at[index,'coordinates_list'] = [[long, lat]]
        else:
            long, lat = geocode(row['area'])
            df.at[index,'coordinates_list'] = [[long, lat]]

#%% Organize different geometries into spatially-enabled dataframes


for index, row in df.iterrows():
    if len(row['coordinates_list'])==1:
        df.at[index,'derived_geometry']='Point'
        df.at[index,'SHAPE']={'spatialReference': {'wkid': 4326}, 'x': row['coordinates_list'][0][0], 'y': row['coordinates_list'][0][1]}
    elif len(row['coordinates_list'])==2:
        df.at[index,'derived_geometry']='Line'
        df.at[index,'SHAPE']={"paths": [row['coordinates_list']],"spatialreference" : {"wkid" : 4326}}
    elif len(row['coordinates_list'])==0:
        df.at[index,'derived_geometry']='Unknown'
    else:
        count = sum( [ len(listElem) for listElem in row['coordinates_list']])
        print(row['area'], count)
        df.at[index,'derived_geometry']='Polygon'
        if count == 5 or count == 9 or count == 14 or count == 13:
            df.at[index,'SHAPE']={"rings": df.at[index,'coordinates_list'][1:], "spatialreference" : {"wkid" : 4326}}
        else:
            print(row['area'],str())
            df.at[index,'SHAPE']={"rings": [df.at[index,'coordinates_list']], "spatialreference" : {"wkid" : 4326}}

#%% Connect to and push to uCOP

tokens = pd.read_csv(r"C:\Users\M3ECHJJJ\Documents\Tokens.csv", index_col='Site')
gis = GIS(tokens.at['uCOP','URL'])
layer_item = gis.content.get('a95daa4bfe1c4ca0b91faa97706a66a7')
layers = layer_item.layers
point_flayer = layers[0]
line_flayer = layers[1]
poly_flayer = layers[2]
tables = layer_item.tables
table_flayer = tables[0]

poly_sdf =pd.DataFrame.spatial.from_layer(poly_flayer)
poly_ids = [str(row['objectid']) for value, row in poly_sdf.iterrows()]
table_sdf =pd.DataFrame.spatial.from_layer(table_flayer)
table_ids = [str(row['objectid']) for value, row in table_sdf.iterrows()]
point_sdf =pd.DataFrame.spatial.from_layer(point_flayer)
point_ids = [str(row['objectid']) for value, row in point_sdf.iterrows()]
line_sdf =pd.DataFrame.spatial.from_layer(line_flayer)
line_ids = [str(row['objectid']) for value, row in line_sdf.iterrows()]

df['POINT_SHAPE']=''
point_df = df
line_df = df[df.derived_geometry.isin(['Line'])]
poly_df = df[df.derived_geometry.isin(['Polygon'])]
for index, row in df.iterrows():
    df.at[index,'POINT_SHAPE']={'spatialReference': {'wkid': 4326}, 'x': row['coordinates_list'][0][0], 'y': row['coordinates_list'][0][1]}

def assemble_point_updates(row):
    try:
        add_feature = {}
        for col in df.columns:
            add_feature[col.lower()] = row[col]
        feat = {'geometry':row['POINT_SHAPE'],'attributes': add_feature}
        adds_to_push.append(feat)
    except:
        pass
def assemble_feature_updates(row):
    try:
        add_feature = {}
        for col in df.columns:
            add_feature[col.lower()] = row[col]
        feat = {'geometry':row['SHAPE'],'attributes': add_feature}
        adds_to_push.append(feat)
    except:
        pass

adds_to_push = []
point_df.apply(lambda row: assemble_point_updates(row), axis=1)
point_update_result = point_flayer.edit_features(adds=adds_to_push, deletes=point_ids, rollback_on_failure=False)
point_update_result
adds_to_push = []
line_df.apply(lambda row: assemble_feature_updates(row), axis=1)
line_update_result = line_flayer.edit_features(adds=adds_to_push,deletes=line_ids, rollback_on_failure=False)

adds_to_push = []
poly_df.apply(lambda row: assemble_feature_updates(row), axis=1)
poly_update_result = poly_flayer.edit_features(adds=adds_to_push, deletes=poly_ids, rollback_on_failure=False)

#############################TESTING AREA######################################
df
