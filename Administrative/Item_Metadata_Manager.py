#%%
from arcgis import GIS
import pandas as pd
tokens = pd.read_csv(r"C:\Users\M3ECHJJJ\Documents\Github\Tokens.csv", index_col='Site')

#%%
termstoadd = '<i>While the United States Army Corps of Engineers (hereinafter referred to USACE) has made a reasonable effort to insure the accuracy of the maps and associated data, it should be explicitly noted that USACE makes no warranty, representation or guaranty, either express or implied, as to the content, sequence, accuracy, timeliness or completeness of any of the data provided herein. The USACE, its officers, agents, employees, or servants shall assume no liability of any nature for any errors, omissions, or inaccuracies in the information provided regardless of how caused. The USACE, its officers, agents, employees or servants shall assume no liability for any decisions made or actions taken or not taken by the user of the maps and associated data in reliance upon any information or data furnished here. By using these maps and associated data the user does so entirely at their own risk and explicitly acknowledges that he/she is aware of and agrees to be bound by this disclaimer and agrees not to present any claim or demand of any nature against the USACE, its officers, agents, employees or servants in any forum whatsoever for any damages of any nature whatsoever that may result from or may be caused in any way by the use of the maps and associated data.</i>'
tagstoadd = ['United States Army Corps of Engineers', 'USACE', 'Galveston District', 'SWD','SWG']
creditstoadd = 'United States Army Corps of Engineers - Galveston District, Engineering and Construction, Geospatial Branch'
desctoadd = '''<span style="font-family:&quot;Avenir Next W01&quot;, &quot;Avenir Next W00&quot;, &quot;Avenir Next&quot;, Avenir, &quot;Helvetica Neue&quot;, sans-serif; background-color:rgb(255, 255, 0);"><font color="#000000" size="3" style>Input description of the content here and how often it is updated.</font></span><div><font face="Avenir Next W01, Avenir Next W00, Avenir Next, Avenir, Helvetica Neue, sans-serif" size="3"><br /></font><div><font size="3"><b><font color="#000000" style="font-family:inherit;">Data Source(s) </font></b></font></div><div><font color="#000000" style="font-size:medium; text-indent:-0.25in; background-color:rgb(255, 255, 0);">Input list of data sources here.</font><font size="3"><b><font color="#000000" style="font-family:inherit;"><br /></font></b></font></div><div><font color="#000000" style="font-size:medium; text-indent:-0.25in; background-color:rgb(255, 255, 0);"><br /></font></div><div><div><font size="3"><b><font color="#000000" style="font-family:inherit;">Customer(s) <br /></font></b><span style="font-family:Arial, sans-serif; color:rgb(59, 56, 56);">The dashboard was
requested by <span style="background:yellow;">Unknown</span>
for inclusion into the TITLE on <span style="background:yellow;">Unknown</span> date</span><span style="font-family:&quot;inherit&quot;, serif; color:rgb(118, 113, 113);">.</span><b><font color="#000000" style="font-family:inherit;"><br /></font></b></font></div></div><div><font color="#000000" style="font-size:medium; text-indent:-0.25in; background-color:rgb(255, 255, 0);"><br /></font></div><div><div style="font-family:&quot;Avenir Next W01&quot;, &quot;Avenir Next W00&quot;, &quot;Avenir Next&quot;, Avenir, &quot;Helvetica Neue&quot;, sans-serif;"><font style="font-family:inherit;"><div style="font-family:inherit;"><div style="font-family:inherit;"><b><font color="#000000" size="3" style="font-family:inherit;">Contact Information</font></b></div><div style="font-family:inherit;"><font size="3"><i><span style="font-family:Arial, sans-serif; color:rgb(59, 56, 56);">Please reach out to </span></i><i><u><span style="font-family:Arial, sans-serif; color:rgb(68, 114, 196);">ceswg-ecg-geospatial@usace.army.mil</span></u></i><i><span style="font-family:Arial, sans-serif; color:rgb(68, 114, 196);"> </span></i><i><span style="font-family:Arial, sans-serif; color:rgb(59, 56, 56);">with any questions/concerns.</span></i></font></div></div></font></div><p style="text-indent:-.25in;"><font size="3"><span style="text-indent:-0.25in; background-image:initial; background-position:initial; background-size:initial; background-repeat:initial; background-attachment:initial; background-origin:initial; background-clip:initial;"></span></font></p><div style="font-family:&quot;Avenir Next W01&quot;, &quot;Avenir Next W00&quot;, &quot;Avenir Next&quot;, Avenir, &quot;Helvetica Neue&quot;, sans-serif;"><b><font color="#000000" style="font-family:inherit;">Release Notes<br /></font></b><span style="font-size:medium; font-family:Arial, sans-serif; color:rgb(59, 56, 56); background-color:rgb(255, 255, 0);">Unknown</span><br /></div><span style="font-family:&quot;Avenir Next W01&quot;, &quot;Avenir Next W00&quot;, &quot;Avenir Next&quot;, Avenir, &quot;Helvetica Neue&quot;, sans-serif; font-size:16px;"></span></div></div>'''
summarytoadd = 'This TYPE of TITLE was developed by the USACE Galveston District Geospatial Team.'







#%%
def credits(flt,size):
    if flt == 'Feature Service':
        usage = (size/10)*2.4
    else:
        usage = (size/1200)*1.2
    return(usage)

#%%

portals = {'SWD-EM': [tokens.at['SWD-EM','Username'], tokens.at['SWD-EM','Password']],
           'USACE-SWG': [tokens.at['USACE-SWG','Username'], tokens.at['USACE-SWG','Password']], 
           'CESWG': [tokens.at['CESWG','Username'], tokens.at['CESWG','Password']]}


#%%
df = pd.DataFrame(columns = ['Name', 'Owner','Summary','Status','Description','Tags','Type','Categories','Created','Terms_of_use','ItemID','Access','Size','Credit_Consumption','Credits','Platform']) 


#%%
for key, value in portals.items():
    print('Signing into', key)
    gis = GIS(username=value[0], password=value[1])
    contents = gis.content.search('',max_items=10000)
    for count, item in enumerate(contents):
        try:
            cpm = credits(item.type, item.size*0.000001)
            df=df.append({'Name':item.title,
            'Owner':item.owner,
            'Description':item.description,
            'Tags':str(item.tags).strip("[").strip("]").replace("'",""),
            'Summary':item.snippet,
            'Terms_of_use':item.licenseInfo,
            'Type':item.type,
            'Categories':str(item.categories).strip("[").strip("]"),
            'Created':item.created,
            'Status':item.content_status,
            'ItemID':item.id,
            'Access':item.access,
            'Views_Total':item.numViews,
            'Size':item.size*0.000001,
            'Credits':item.accessInformation,
            'Credit_Consumption':cpm,
            'Platform':key},ignore_index=True)
            print('Progress: ', count, 'of', len(contents), end='\r')
        except Exception:
            pass


    df1= df[df['Terms_of_use'].isnull() = df['Credits'] | df['Summary'].isnull() | df['Description'].isnull() | df['Tags'].str.len() < 3]
    df1 = df1[df1['Platform']==key].reset_index(drop=True)

    for index, row in df1.iterrows():
        try:
            item = gis.content.get(row['ItemID'])
            updates = {}
            if row['Description']=='' or row['Description'] is  None:
                updates['description']=desctoadd.replace('TITLE',item.title)
            if row['Summary']=='' or row['Summary'] is None:
                updates['snippet']=summarytoadd.replace('TITLE',item.title).replace('TYPE',item.type)
            if row['Credits']=='' or row['Credits'] is None:
                updates['accessInformation']=creditstoadd
            if row['Terms_of_use']=='' or row['Terms_of_use'] is None:
                updates['licenseInfo']=termstoadd
            if len(item.tags)<3:
                tags_list = [*item.tags, *tagstoadd] 
                temp = list(map(str, tags_list)) 
                res = ", ".join(temp)
                updates['tags']=str(res)

            i = item.update(item_properties=updates)
        except Exception as e:
            print(e)
        print('Progress: ', index, 'of', len(df1), end='\r')

 #%%
