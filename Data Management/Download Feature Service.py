itemid = '1cc027acc4f04aca8e5b6ddd6bbea287'
pathtodownload = r'C:\Users\M3ECHJJJ\Documents'

from arcgis import GIS
import pandas as pd
import os

gis = GIS("home")
layer_item = gis.content.get(itemid)
layers = layer_item.layers
tables = layer_item.tables
path1 = os.path.join(pathtodownload, layer_item.title)
isExist = os.path.exists(path1)
if not isExist:
    os.mkdir(path1)

for flayer in layers:
    print('Downloading layer: ', flayer.properties.name)
    oid = flayer.properties.objectIdField
    path2 = os.path.join(path1, flayer.properties.name)
    isExist = os.path.exists(path2)
    if not isExist:
        os.mkdir(path2)
    df = flayer.query().sdf
    df.to_csv(os.path.join(path2, flayer.properties.name + '.csv'))
    featureset = df.spatial.to_featureset()
    with open(os.path.join(path2, flayer.properties.name + '.geojson'), "w", encoding="utf-8") as file:
        file.write(featureset.to_geojson)
    if flayer.properties.hasAttachments:
        print("    Searching and downloading attachments:")
        for index, row in df.iterrows():
            print('\r        ' + str(index + 1) + "/" + str(len(df)), end="")
            attList = flayer.attachments.get_list(oid=row[oid])
            if len(attList) > 0:
                path3 = os.path.join(path2, str(row[oid]))
                isExist = os.path.exists(path3)
                if not isExist:
                    os.mkdir(path3)
                for att in attList:
                    if not os.path.exists(os.path.join(path3, att['name'])):
                        flayer.attachments.download(row[oid], attachment_id=att['id'], save_path=path3)
    else:
        print('    Attachments not enabled on layer, skipping search')

for ftable in tables:
    print('Downloading table: ', ftable.properties.name)
    oid = ftable.properties.objectIdField
    path2 = os.path.join(path1, ftable.properties.name)
    isExist = os.path.exists(path2)
    if not isExist:
        os.mkdir(path2)
    df = ftable.query().sdf
    df.to_csv(os.path.join(path2, ftable.properties.name + '.csv'))
    if ftable.properties.hasAttachments:
        print("    Searching and downloading attachments:")
        for index, row in df.iterrows():
            print('\r        ' + str(index + 1) + "/" + str(len(df)), end="")
            attList = ftable.attachments.get_list(oid=row[oid])
            if len(attList) > 0:
                path3 = os.path.join(path2, str(row[oid]))
                isExist = os.path.exists(path3)
                if not isExist:
                    os.mkdir(path3)
                for att in attList:
                    if not os.path.exists(os.path.join(path3, att['name'])):
                        ftable.attachments.download(row[oid], attachment_id=att['id'], save_path=path3)
    else:
        print('    Attachments not enabled on layer, skipping search')
