import numpy as np
import pandas as pd
import xarray as xr
import netCDF4
from erddapy import ERDDAP
import json

with open('ra_erddaps.json') as f:
    urls = json.load(f)

df = pd.read_excel('../2020/data/raw/Asset Inventory_PacIOOS_2020.xlsx',sheet_name=1)
#
# df_cruise = df[df['Station Description'] == 'Chesapeake Bay WQ Cruise Data ']
# df_wf = df[df['Station Description'] == 'WeatherFlow Meteorological Station']
df_aws = df[df['Station ID'] == 'CWB-NSS 1']
# #url = 'http://tds.glos.us/thredds/dodsC/buoy_agg_standard/OMOECC_E1/OMOECC_E1.ncml'
# #url = 'http://tds.glos.us/thredds/dodsC/buoy_agg_standard/45186/45186.ncml'
# #url = 'http://tds.glos.us/thredds/dodsC/buoy_agg_standard/bgsusd2/bgsusd2.ncml'
# url = 'http://oos.soest.hawaii.edu/thredds/dodsC/hioos/nss/ns12agg'
# print(url)
# ds = xr.open_dataset(url)
# #ds = netCDF4.Dataset(url,'r')
# title = ds.title
# start_time = np.datetime_as_string(ds.time.min().values, unit='D')
# end_time = np.datetime_as_string(ds.time.max().values, unit='D')
# print('Duration: %s - %s' % (np.datetime_as_string(ds.time.min().values, unit='D'),
#                              np.datetime_as_string(ds.time.max().values, unit='D'))
#       )

# Try glos web server
# url = 'https://glbuoys.glos.us/tools/export?ftype=csv&data_type=buoy&units=eng&locs=OMOECC_E1&params=Water_Temperature_at_Surface|dissolved_oxygen_saturation|water_conductivity|ysi_turbidity&tperiod=custom&date_start=2020-01-01&date_end=2020-12-31&avg_ivld=none'
# df = erddapy.ERDDAP.to_pandas(url)

## using ERDDAP to look for stations
# check out http://data.glos.us/erddap/tabledap/allDatasets.htmlTable?datasetID%2Ctitle%2CminTime%2CmaxTime&maxTime%3E=2020-01-01&maxTime%3C=2020-12-31&orderBy(%22maxTime%22)
# that lists out all the GLOS stations with the maximum time of observations within the year 2020 (on their ERDDAP).

server = urls['pacioos2']
e = ERDDAP(server=server, protocol="tabledap")
for index, row in df_aws.iterrows():
    id = row['Station ID'].replace('CWB-NSS 1', 'NSS-CWB-001')
    e.dataset_id = id
    e.constraints = {
        "time>=": "2020-01-01",
        "time<=": "2020-12-31"
    }
    title = e.dataset_id
# # url = 'http://data.glos.us/erddap/tabledap/osugi.csv'
    df_data = e.to_pandas(parse_dates=True)
# drop qc vars
    cols = [c for c in df_data.columns if 'qc' not in c]
    df_data = df_data[cols]
# set index for plotting
    df_data = df_data.set_index(df_data['time (UTC)'])
# plot
    df_data.plot(subplots=True)

    start_time = df_data['time (UTC)'].min()
    end_time = df_data['time (UTC)'].max()



    print('Dataset %s' % title)
    print('Duration: %s - %s' % (start_time, end_time))