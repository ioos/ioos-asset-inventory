import pandas as pd
import numpy as np
import os

files = os.listdir('data/raw/Original RA submissions')
print('Found %i Excel workbooks' % len(files))
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
    print(file, len(df.columns))
    print(df.columns)

# drop superfluous headers buried during concatenation
df_all.drop(df_all.loc[df_all['Latitude (dec deg)'] == '(Required) '].index, inplace=True)

# find rows missing RA name
idx = df_all[df_all['RA'].isin([np.nan, ''])].index

# insert RA name, when missing, by extracting from the file name
df_all.loc[idx, 'RA'] = df_all.loc[idx, 'file'].str.replace(
    'Observing_Asset_Inventory_', '').str.replace(
    '_Dec2019.xlsx', '').str.replace(
    '_Asset_Inventory_2019.xlsx', '').str.replace(
    'revised_Final_', '').str.replace(
    ' Asset Inventory_2019-2nd submission.xlsx', '').replace(' ', '')

## Remove the useless rows
df_all.drop(
    df_all.loc[
        (df_all['RA'] == 'AOOS') & (df_all['Station ID'].str.contains('Something'))].index,
    inplace=True)

df_all.drop(
    df_all.loc[
        (df_all['RA'] == 'AOOS') & (df_all['Station ID'].str.contains('Removed'))].index,
    inplace=True)

# TODO find non-numeric latitude/longitude rows. Need to adjust to only search specific columns
df_all[~df_all.applymap(np.isreal).all(1)]