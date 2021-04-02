import pandas as pd
import os
import geopandas
import matplotlib.pyplot as plt
import fiona

fiona.drvsupport.supported_drivers['KML'] = 'rw' # enable KML support which is disabled by default

## For 2020
dir = 'data/processed/'
files = os.listdir(dir)
print('Found %i Excel workbooks' % len(files))

df_raw = pd.DataFrame(
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
    fname = dir + file

    print('Reading %s' % file)
    df = pd.read_excel(fname, header=0)

    # Drop empty rows
    df.dropna(axis='index', how='all', inplace=True)
    # Removing special chars
    df.replace('\xa0', '', regex=True, inplace=True)

    # create RA column if missing
    if 'RA' not in df.columns:
        df['RA'] = ''

    # add the file name for use later
    df['file'] = file

    # concatenate data frames into one mongo DF.
    df_raw = pd.concat([df_raw, df], ignore_index=True)

    # print some information out
    print('Ingested %s with %i columns' % (file, len(df.columns)))

print('Initial row count: %i' % df_raw.shape[0])

# create a copy of the dataFrame for processing
df_all = df_raw.copy()

print('Removing platform type = \'surface_current_radar\' | \'glider\'.')
df_all.drop(
    df_all.loc[
        (df_all['Platform Type'] == 'surface_current_radar') |
        (df_all['Platform Type'] == 'glider')
    ].index,
    inplace=True)
print('row count:', df_all.shape[0])

# convert lat/lon to floating points
df_all[['Latitude (dec deg)', 'Longitude (dec deg)']] = df_all[['Latitude (dec deg)', 'Longitude (dec deg)']].astype(float)

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

## Make a simple plot of station locations
gdf = geopandas.GeoDataFrame(
    df_all, geometry=geopandas.points_from_xy(df_all['Longitude'], df_all['Latitude']))
world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
ax = world.plot(
    color='white', edgecolor='black')
gdf.plot(ax=ax, color='red', markersize=1)
plt.show()

# Create a final data frame for processed file
df_final = pd.DataFrame(columns=
                        ['RA','Latitude','Longitude','Platform','Operational',
                         'RA_Funded','Water_temp','Salinity','Wtr_press',
                         'Dew_pt','Rel_hum','Air_temp','Winds','Air_press',
                         'Precip','Solar_radn','Visibility','Water_level','Waves',
                         'Currents','Turbidity','DO','pCO2_water','pCO2_air','TCO2',
                         'pH','OmgArag_st','Chl','Nitrate','CDOM','Alkalinity','Acoustics'])

df_final['RA'] = df_all['RA']
df_final['station_long_name'] = df_all['Station Long Name']
df_final['Latitude'] = df_all['Latitude']
df_final['Longitude'] = df_all['Longitude']
df_final['Platform'] = df_all['Platform Type']
df_final['Operational'] = df_all['Currently Operational? (Y, N, O, U)']
df_final['RA_Funded'] = df_all['RA Funding Involvement (Yf, Yp, N)']
df_final['Raw_Vars'] = df_all['Variable Names']

# TODO clean up the platform types
# Unique list of plaform types
plat_lut = {
    'moored_buoy': 'moored_buoy',
    'Fixed moored_buoy': 'moored_buoy',
    'Fixed': 'fixed',
    'fixed': 'fixed',
    'wave_buoy': 'wave_buoy',
    'Fixed shorebased': 'fixed',
    'Moored wave buoy': 'wave_buoy',
    'Moored Buoy': 'moored_buoy',
    'fixed ': 'fixed',
    'offshore_tower': 'tower',
    'tide_station': 'tide_station',
    'offshore_platform': 'offshore_platform',
    'tower': 'tower',
    'buoy and mooring': 'moored_buoy',
    'profiling_buoy': 'profiling_buoy',
    'river_level_station': 'river_level_station',
    'mooring': 'moored_buot',
    'buoy ': '',
    'ship': '',
    'sampling_location': '',
    'mooring ': '',
    'glider': '',
    'surface_current_radar': '',
    'bottom_mount': ''
}

# map provided variable text to standard vars
var_lut = {
    'Water_temp': 'sea_water_temperature',
    'Salinity': 'salinity',
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
    'pH': 'pH|sea_water_ph_reported_on_total_scale',
    'OmgArag_st': 'aragonite',
    'Chl': 'chlorophyll',
    'Nitrate': 'nitrate',
    'CDOM': 'blue_green_algae|colored_dissolved_organic_matter',
    'Alkalinity': 'alkalinity',
    'Acoustics': 'acoustic',
    }
# Insert True for assets that have text in 'Variable Names' from mapping above
for key in var_lut:
    df_final[key] = df_all['Variable Names'].str.contains(var_lut[key], na=False)

df_final.replace(False, '', inplace=True)
df_final.replace(True, 'X', inplace=True)

# reorganize df
cols = ['RA', 'Latitude', 'Longitude', 'station_long_name', 'Platform', 'Operational', 'RA_Funded',
        'Water_temp', 'Salinity', 'Wtr_press', 'Dew_pt', 'Rel_hum', 'Air_temp',
        'Winds', 'Air_press', 'Precip', 'Solar_radn', 'Visibility',
        'Water_level', 'Waves', 'Currents', 'Turbidity', 'DO', 'pCO2_water',
        'pCO2_air', 'TCO2', 'pH', 'OmgArag_st', 'Chl', 'Nitrate', 'CDOM',
        'Alkalinity', 'Acoustics', 'Raw_Vars']
df_final = df_final[cols]

# Create a geopandas dataframe and save as geojson
gdf_final = geopandas.GeoDataFrame(
    df_final, geometry=geopandas.points_from_xy(df_final['Longitude'], df_final['Latitude']))

# Write data
# print('Saving inventory files...')
# # csv
# df_raw.to_csv('combined_raw_inventory.csv', index=False)
# df_final.to_csv('processed_inventory.csv', index=False)
# # geojson
# gdf.to_file('combined_raw_inventory.geojson', driver='GeoJSON')
# gdf_final.to_file('processed_inventory.geojson', driver='GeoJSON')
# # kml
# gdf.to_file('combined_raw_inventory.kml', driver='KML')
# gdf_final.to_file('processed_inventory.kml', driver='KML')
