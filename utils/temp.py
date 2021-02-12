import numpy as np
import pandas as pd
import xarray as xr
import netCDF4
from erddapy import ERDDAP

# #url = 'http://tds.glos.us/thredds/dodsC/buoy_agg_standard/OMOECC_E1/OMOECC_E1.ncml'
# #url = 'http://tds.glos.us/thredds/dodsC/buoy_agg_standard/45186/45186.ncml'
# #url = 'http://tds.glos.us/thredds/dodsC/buoy_agg_standard/bgsusd2/bgsusd2.ncml'
# url = 'http://thredds.secoora.org/thredds/dodsC/secoora/sensors/gov_fl_fldep_8722213/data/sea_water_temperature.nc'
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

server = 'http://erddap.secoora.org/erddap'
e = ERDDAP(server=server, protocol="tabledap")
e.dataset_id = 'edu_northcarolina_csi_44095'
e.constraints = {
    "time>=": "2020-01-01",
    "time<=": "2020-12-31"
}
title = e.dataset_id
# # url = 'http://data.glos.us/erddap/tabledap/osugi.csv'
df = e.to_pandas(parse_dates=True)
# drop qc vars
cols = [c for c in df.columns if 'qc' not in c]
df = df[cols]
# set index for plotting
df = df.set_index(df['time (UTC)'])
# plot
df.plot(subplots=True)

start_time = df['time (UTC)'].min()
end_time = df['time (UTC)'].max()



print('Dataset %s' % title)
print('Duration: %s - %s' % (start_time, end_time))