import os
import glob
import sys
import numpy as np
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
import cdsapi
from netCDF4 import Dataset
from cftime import num2date, date2num, date2index

# Harry's Code:
import U_regrid as rg
import U_config as cfg

# =========== CDS Acronym Dictionary ===========
CDS_DICT = {"sea_surface_temperature":"sst", "2m_temperature":"t2m", "mean_sea_level_pressure":"msl", "geopotential":"z", "surface_net_solar_radiation":"ssr", "surface_solar_radiation_downwards": "ssrd", "10m_u_component_of_wind" : "u10", "10m_v_component_of_wind" : "v10" }
START_YEAR = 1979
END_YEAR = 2022

def retrieve_data(variable, years, area, file_location):
    print(f'\nCommencing data download for {variable}...')
    cds = cdsapi.Client()
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    
    cds_params = {
        'product_type' : 'monthly_averaged_reanalysis',
        'variable': variable,
        'year' : years,
        'month' : months,
        'time' : '00:00',
        'format' : 'netcdf',
        'area' : area
    }

    if (variable == 'geopotential'):
        dataset = 'reanalysis-era5-pressure-levels-monthly-means'   
        cds_params['pressure_level'] = '500'
    else:
        dataset = 'reanalysis-era5-single-levels-monthly-means'

    try:
        print(f'\nSaving data to {file_location}')
        cds.retrieve(dataset, cds_params, file_location)
        print(f'\nData download successful.')
        return True    
    except:
        print(f'\nData download failed.')
    return False

if __name__ == '__main__':
    var = sys.argv[1]
    force_download = sys.argv[2]

    file_loc = os.path.join(cfg.ERA5_RAW, f'{var}_raw_data.nc4')
    if not os.path.isfile(file_loc) or force_download==True:
        years = [str(i) for i in range(START_YEAR, END_YEAR+1)]
        area_vals = [90, -180, -60, 180]
        if not retrieve_data(var, years, area_vals, file_loc):
            raise Exception("Data download has failed.\nPlease check your variable name is correct, the years are valid and that you have setup the CDF account and file on your computer.")

    print(f'\nProcessing {var} .nc4 data...')
    
    # Validation - output what date range is available in the .nc4 file.
    era_data = Dataset(file_loc)    
    times = era_data.variables['time']
    dates = num2date(times[:], times.units)
    start = dates[0].strftime('%Y-%m-%d %H:%M:%S')
    end = dates[-1].strftime('%Y-%m-%d %H:%M:%S') 
    print(f'Found the following date range: {start} - {end}')

    if (dates[0].year > START_YEAR):
        raise Exception("Start year available in the .nc4 file exceeds the specified start year.\n Either alter this constant, of set 'force_download' to TRUE.")
    elif (dates[-1].year < END_YEAR):
        raise Exception("Start year available in the .nc4 file exceeds the specified end year.\n Either alter this constant, of set 'force_download' to TRUE.")

    # Extract for each month BY index to prevent data from being jumbled:
    start_time = dt.datetime(START_YEAR,1,1,0,0)
    end_time = dt.datetime(END_YEAR,12,1,0,0)
    month_delta = (end_time.month - start_time.month) + (12*(end_time.year - start_time.year))
    print(f'Total samples in this date range: {month_delta} starting at {start_time}.\n')
    dates_list  = [start_time + relativedelta(months = m) for m in range(0, month_delta+1)]   
    indices = date2index(dates_list, era_data.variables["time"], calendar="gregorian", select='exact')
    if (len(indices)-1 != month_delta): 
        print('\nThere are missing records. You should investigate further')

    print(f'Regriddding data...')
    regridder = rg.regrid(era_data['latitude'][:], era_data['longitude'][:])

    samples = []
    for idx in indices:
        temp = era_data[CDS_DICT[var]][idx]
        temp = regridder.perform_regridding(temp.T)

        if (var in ["sea_surface_temperature", "2m_temperature"]):
            # Convert to Celsius
            temp[temp<0] = np.nan
            temp = temp - 273.15
        elif (var == "geopotential"):
            # Convert geopotential to geopotential height
            temp = temp / 9.80665
        elif (var == "mean_sea_level_pressure"):
            # Convert Pascals to MilliBars
            temp = temp / 100
        samples.append(temp)

    create_dateset:        
    print(f'\nSaving {var} monthly averages ...\n')
    VAR_FOLDER = os.path.join(cfg.ERA5_PROCESSED, var)
    if not(os.path.isdir(VAR_FOLDER)):
        os.makedirs(VAR_FOLDER)
        
    count = 0
    for idx in indices:
        month_val = dates[idx].month
        month = f'0{month_val}' if (month_val < 10) else month_val
        file_name = f'{dates[idx].year}_{month}.npy'
        save_loc = os.path.join(VAR_FOLDER, file_name)
        np.save(save_loc, samples[count])
        count+=1
