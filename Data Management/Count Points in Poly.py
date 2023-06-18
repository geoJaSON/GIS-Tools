from arcgis import GIS
import pandas as pd
from arcgis.geometry.filters import intersects
tokens = pd.read_csv(r"C:\Users\M3ECHJJJ\Documents\Tokens.csv", index_col='Site')
gis = GIS(tokens.at['uCOP','URL'])
layer_item = gis.content.get('d4b35bba9db94d17896027a9ba5cb56f')
layers = layer_item.layers
flayer = layers[2]
poly= flayer.query().features

flayerp = layers[0]
points = flayerp.query()

parcel_item = gis.content.get('cda676bff37e4761bcc77e322e1164df')
parcellayers = parcel_item.layers
flayerpar = parcellayers[0]


updates_to_push = []


for p in poly:
    try:
        pfilter = intersects(p.geometry)
        pointscount = len(flayerp.query(geometry_filter=pfilter, as_df=True))
        parcelcount = len(flayerpar.query(geometry_filter=pfilter))
        edit_feature = {'objectid': p.attributes['objectid'],'parcels':parcelcount,'roofs':pointscount}
        feat = {'attributes': edit_feature}
        updates_to_push.append(feat)
    except:
        pass

update_result = flayer.edit_features(updates=updates_to_push, rollback_on_failure=False)
