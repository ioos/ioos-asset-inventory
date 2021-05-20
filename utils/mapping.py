def variables(df_final, df_all):
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

    return df_final


def platforms(df_final):
    # Unique list of platform types
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
        'mooring': 'moored_buoy',
        'buoy ': 'moored_buoy',
        'ship': 'ship',
        'sampling_location': '',
        'mooring ': 'moored_buoy',
        'glider': 'glider',
        'surface_current_radar': 'surface_current_radar',
        'bottom_mount': 'moored_buoy'
    }

    df_final['Platform'].replace(plat_lut, inplace=True)

    return df_final

