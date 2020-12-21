import pandas as pd
import numpy as np
import os

files = os.listdir('data/raw/Original RA submissions')
print('Found %i Excel workbooks' % len(files))

print('Dropping %s' % files[4])
files.pop(4)  # remove the initial AOOS submission

df_all = pd.DataFrame(
    columns=['RA', 'Station ID', 'WMO ID or NWS/CMAN ID', 'Station Long Name',
       'Station Description', 'Latitude (dec deg)', 'Longitude (dec deg)',
       'Platform Type', 'Station Deployment (mm/yyyy, yyyy, < 5 yr, > 5 yr)',
       'Currently Operational? (Y, N, O, U)', 'Platform Funder/Sponsor',
       'RA Funding Involvement (Yf, Yp, N)', 'Platform Operator/Owner',
       'Operator Sector', 'Platform Maintainer', 'Data Manager',
       'Variable Names + water column depth of measurement in meters [CF_name (# m, # m) or CF_name (mult) or CF_name (# depths)].',
       'Additional notes', 'file']
)
for file in files:
    fname = 'data/raw/Original RA submissions/' + file

    # NANOOS and PacIOOS' inventories in second sheet
    if any(x in file for x in ['NANOOS', 'PacIOOS']):
        df = pd.read_excel(fname, header=0, sheet_name=1)
    else:
        df = pd.read_excel(fname, header=0)

    # Drop empty rows
    df.dropna(axis='index', how='all', inplace=True)

    # create RA column if missing
    if 'RA' not in df.columns:
        df['RA'] = ''

    # add the file name for use later
    df['file'] = file

    # concatenate data frames into one mongo DF.
    df_all = pd.concat([df_all, df],ignore_index=True)

    # print some information out
    print('Ingested %s with %i columns' % (file, len(df.columns)))
    #print(df.columns)

print('Initial row count: %i' % df_all.shape[0])
# drop superfluous headers buried during concatenation
print('Dropping extra headers...')
df_all.drop(df_all.loc[df_all['Latitude (dec deg)'] == '(Required) '].index, inplace=True)
print('row count:', df_all.shape[0])

# find rows missing RA name
print('Dropping rows missing RA name.')
idx = df_all[df_all['RA'].isin([np.nan, ''])].index
print('row count:', df_all.shape[0])
# insert RA name, when missing, by extracting from the file name

print('Inserting RA name from file name...')
df_all.loc[idx, 'RA'] = df_all.loc[idx, 'file'].str.replace(
    'Observing_Asset_Inventory_', '').str.replace(
    '_Dec2019.xlsx', '').str.replace(
    '_Asset_Inventory_2019.xlsx', '').str.replace(
    'revised_Final_', '').str.replace(
    ' Asset Inventory_2019-2nd submission.xlsx', '').replace(' ', '')

## Remove the useless rows
print('Removing rows where AOOS has the srting \'Something\'.')
df_all.drop(
    df_all.loc[
        (df_all['RA'] == 'AOOS') & (df_all['Station ID'].str.contains('Something'))].index,
    inplace=True)
print('row count:', df_all.shape[0])

print('Removing rows where AOOS has the string \'Removed\'.')
df_all.drop(
    df_all.loc[
        (df_all['RA'] == 'AOOS') & (df_all['Station ID'].str.contains('Removed'))].index,
    inplace=True)
print('row count:', df_all.shape[0])

print('Removing platform type = \'surface_current_meter\'.')
df_all.drop(
    df_all.loc[
        (df_all['Platform Type'] == 'surface_current_radar')
    ].index,
    inplace=True)
print('row_count:', df_all.shape[0])

# find non-numeric latitude/longitude rows. Need to adjust to only search specific columns
# this finds all non-numerics. Need to search lat/lon columns.
print('Dropping non-numeric lat/lons...')
df_all.drop(
    df_all.loc[
        (~df_all['Latitude (dec deg)'].apply(np.isreal)) | (~df_all['Longitude (dec deg)'].apply(np.isreal))
    ].index,
    inplace=True)
print('count:', df_all.shape[0])

print('Dropping invalid lat/lons...')
df_all.drop(
    df_all.loc[
        (df_all['Latitude (dec deg)'] > 90) | (df_all['Longitude (dec deg)'] < -180)
    ].index,
    inplace=True)
print('final count:', df_all.shape[0])
# Write all data to csv file
#df_all.to_csv('2019_Combined_asset_Inventory.csv', index=False)

df_all['Station Deployment (mm/yyyy, yyyy, < 5 yr, > 5 yr)'] = \
    df_all['Station Deployment (mm/yyyy, yyyy, < 5 yr, > 5 yr)'].astype(str)

import geopandas
import matplotlib.pyplot as plt

gdf = geopandas.GeoDataFrame(
    df_all, geometry=geopandas.points_from_xy(df_all['Longitude (dec deg)'], df_all['Latitude (dec deg)']))

world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))

# We restrict to South America.
ax = world.plot(
    color='white', edgecolor='black')

# We can now plot our ``GeoDataFrame``.
gdf.plot(ax=ax, color='red')

plt.show()

gdf.to_file("assets.geojson", driver='GeoJSON')