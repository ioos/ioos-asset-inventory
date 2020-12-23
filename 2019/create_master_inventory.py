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

print('Removing platform type = \'surface_current_meter\' | \'glider\'.')
df_all.drop(
    df_all.loc[
        (df_all['Platform Type'] == 'surface_current_radar') |
        (df_all['Platform Type'] == 'glider')
    ].index,
    inplace=True)
print('row count:', df_all.shape[0])

# Write all data to csv file
print('Saving to csv..')
df_all.to_csv('2019_Combined_raw_asset_Inventory.csv', index=False)

## clean data for geojson
# find and remove non-numeric and invalid latitude/longitude rows for geojson.
print('Dropping non-numeric lat/lons for geojson...')
df_all.drop(
    df_all.loc[
        (~df_all['Latitude (dec deg)'].apply(np.isreal)) | (~df_all['Longitude (dec deg)'].apply(np.isreal))
    ].index,
    inplace=True)
print('row count:', df_all.shape[0])

print('Dropping invalid lat/lons...')
df_all.drop(
    df_all.loc[
        (df_all['Latitude (dec deg)'] > 90) | (df_all['Longitude (dec deg)'] < -180)
    ].index,
    inplace=True)
print('final count:', df_all.shape[0])

# saving dates as strings
df_all['Station Deployment (mm/yyyy, yyyy, < 5 yr, > 5 yr)'] = \
    df_all['Station Deployment (mm/yyyy, yyyy, < 5 yr, > 5 yr)'].astype(str)

# rename columns
df_all.rename(columns=
{'Variable Names + water column depth of measurement in meters [CF_name (# m, # m) or CF_name (mult) or CF_name (# depths)].':
     'Variable Names',
 'Station Deployment (mm/yyyy, yyyy, < 5 yr, > 5 yr)': 'Station Deployment',
 'Longitude (dec deg)': 'Longitude',
 'Latitude (dec deg)': 'Latitude'},
              inplace=True)

## Make a plot and write the raw geojson file
import geopandas
import matplotlib.pyplot as plt

gdf = geopandas.GeoDataFrame(
    df_all, geometry=geopandas.points_from_xy(df_all['Longitude'], df_all['Latitude']))

world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))

# create world map
ax = world.plot(
    color='white', edgecolor='black')

# We can now plot our ``GeoDataFrame``.
gdf.plot(ax=ax, color='red')

plt.show()

gdf.to_file("compiled_raw_assets.geojson", driver='GeoJSON')

# Create a final data frame
df_final = pd.DataFrame(columns=
                        ['RA','Latitude','Longitude','Platform','Operational',
                         'RA_Funded','Water_temp','Salinity','Wtr_press',
                         'Dew_pt','Rel_hum','Air_temp','Winds','Air_press',
                         'Precip','Solar_radn','Visibility','Water_level','Waves',
                         'Currents','Turbidity','DO','pCO2_water','pCO2_air','TCO2',
                         'pH','OmgArag_st','Chl','Nitrate','CDOM','Alkalinity','Acoustics'])

df_final['RA'] = df_all['RA']
df_final['Latitude'] = df_all['Latitude']
df_final['Longitude'] = df_all['Longitude']
df_final['Platform'] = df_all['Platform Type']
df_final['Operational'] = df_all['Currently Operational? (Y, N, O, U)']
df_final['RA_Funded'] = df_all['RA Funding Involvement (Yf, Yp, N)']
df_final['Raw_Vars'] = df_all['Variable Names']
# Unique list of variable names
vars = pd.DataFrame(data=sorted(set(sum(df_all['Variable Names'].fillna('').str.replace('\(.*\)','').str.replace(' ','').str.replace('\\n','').str.split(',').tolist(),[]))))
# map provided text to standard vars
mapping = {
    'Water_temp': 'sea_water_temperature',
    'Salinity': 'sea_water_salinity',
    'Wtr_press': 'water_pressure|sea_water_pressure|sea_water_depth',
    'Dew_pt': 'dew_point_temperature|dew_point_temperaure',
    'Rel_hum': 'RelativeHumidity|relative_humidity',
    'Air_temp': 'air_temperature|air_temperatue|atmospheric_temperature',
    'Winds': 'wind|gust',
    'Air_press': 'air_pressure|barometric|surface_air_pressure',
    'Precip': 'precipitation|rainfall_amount',
    'Solar_radn': 'shortwave_flux_in_air|downwelling_photosynthetic_radiance_in_sea_water|photosynthetically_active_radiation|solar|photon',
    'Visibility': 'visibility',
    'Water_level': 'river_level|sea_floor_depth_below_sea_surface|sea_surface_height|water_level|water_surface_height',
    'Waves': 'wave',
    'Currents': 'sea_water_velocity|current|sea_water_speed|sea_water_to_direction',
    'Turbidity': 'turbidity',
    'DO': 'oxygen',
    'pCO2_water': 'mole_fraction_of_carbon_dioxide_in_sea_water|pCO2|partial_pressure_of_carbon_dioxide_in_sea_water|pco2',
    'pCO2_air': 'mole_fraction_of_carbon_dioxide_in_air|partial_pressure_of_carbon_dioxide_in_atmosphere|surface_partial_pressure_of_carbon_dioxide_in_air',
    'TCO2': 'dissolved_carbon_dioxide',
    'pH': 'pH',
    'OmgArag_st': 'aragonite',
    'Chl': 'chlorophyll',
    'Nitrate': 'nitrate',
    'CDOM': 'blue_green_algae|colored_dissolved_organic_matter',
    'Alkalinity': 'alkalinity',
    'Acoustics': 'acoustic',
    }
# Insert True for assets that have text in 'Variable Names' from mapping above
for key in mapping:
    df_final[key] = df_all['Variable Names'].str.contains(mapping[key], na=False)

df_final.replace(False, '', inplace=True)
df_final.replace(True, 'X', inplace=True)

# Create a geopandas dataframe and save as geojson
gdf_final = geopandas.GeoDataFrame(
    df_final, geometry=geopandas.points_from_xy(df_final['Longitude'], df_final['Latitude']))
gdf_final.to_file("compiled_assets_forArcGIS.geojson", driver='GeoJSON')

# export final data frame as csv
df_final.to_csv('2019_Combined_asset_Inventory_forArcGIS.csv', index=False)
