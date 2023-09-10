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

def normalise(data):
    data = np.asarray(data)
    min = np.nanmin(data)
    max = np.nanmax(data)
    return ((data - min)/ (max-min))

if __name__ == '__main__':  
    down_file_loc = os.path.join(cfg.ERA5_RAW, f"surface_solar_radiation_downwards_raw_data.nc4")
    net_file_loc = os.path.join(cfg.ERA5_RAW, f"surface_net_solar_radiation_raw_data.nc4")
    
    net_data = Dataset(net_file_loc)    
    down_data = Dataset(down_file_loc)

    times = net_data.variables['time']
    dates = num2date(times[:], times.units)
    start = dates[0].strftime('%Y-%m-%d %H:%M:%S')
    end = dates[-1].strftime('%Y-%m-%d %H:%M:%S') 
    start_time = dt.datetime(START_YEAR,1,1,0,0)
    end_time = dt.datetime(END_YEAR,12,1,0,0)
    month_delta = (end_time.month - start_time.month) + (12*(end_time.year - start_time.year))
    dates_list  = [start_time + relativedelta(months = m) for m in range(0, month_delta+1)]   
    indices = date2index(dates_list, net_data.variables["time"], calendar="gregorian", select='exact')

    print(f'Regriddding data...')
    regridder_net = rg.regrid(net_data['latitude'][:], net_data['longitude'][:])
    regridder_down = rg.regrid(down_data['latitude'][:], down_data['longitude'][:])

    n_sample = []
    d_sample = []
    u_sample = []
    for idx in indices:
        
        temp_d = down_data['ssrd'][idx]
        temp_d = regridder_down.perform_regridding(temp_d.T)
        
        temp_n = net_data['ssr'][idx]
        temp_n = regridder_net.perform_regridding(temp_n.T)
        
        upwards = (temp_d - temp_n) / (60 * 60 * 24)
        u_sample.append(upwards)
        d_sample.append(temp_d/ (60*60*24))
        n_sample.append(temp_n/(60*60*24))

    #print(f'\nSaving upwards radiation monthly averages ...\n')
    #VAR_FOLDER = os.path.join(cfg.ERA5_PROCESSED, "surface__solar_radiation_upwards")
    #if not(os.path.isdir(VAR_FOLDER)):
    #    os.makedirs(VAR_FOLDER)
        
    #count = 0
    #for idx in indices:
    #    month_val = dates[idx].month
    #    month = f'0{month_val}' if (month_val < 10) else month_val
    #    file_name = f'{dates[idx].year}_{month}.npy'
    #    save_loc = os.path.join(VAR_FOLDER, file_name)
    #    np.save(save_loc, samples[count])
    #   count+=1

    start_time = dt.datetime(1979,1,1,0,0)
    end_time = dt.datetime(2010,12,1,0,0)
    month_delta = (end_time.month - start_time.month) + (12*(end_time.year - start_time.year))

    u_pre_training = normalise(u_sample[0:month_delta+1])
    u_post_training = normalise(u_sample[month_delta+1:])

    n_pre_training = normalise(n_sample[0:month_delta+1])
    n_post_training = normalise(n_sample[month_delta+1:])
    
    d_pre_training = normalise(d_sample[0:month_delta+1])
    d_post_training = normalise(d_sample[month_delta+1:])
    
    print(f'\nSaving normalised data...\n')
    PRE = os.path.join(cfg.DATASET_FOLDER, "pre")
    POST = os.path.join(cfg.DATASET_FOLDER, "pre")
    
    UP_PRE = os.path.join(PRE, "upwards_rad")
    DOWN_PRE = os.path.join(PRE, "downwards_rad")
    NET_PRE = os.path.join(PRE, "net_rad")

    UP_POST = os.path.join(POST, "upwards_rad")
    DOWN_POST = os.path.join(POST, "downwards_rad")
    NET_POST = os.path.join(POST, "net_rad")

    Paths = [UP_PRE, DOWN_PRE, NET_PRE, UP_POST, DOWN_POST, NET_POST]

    for path in Paths:
        if not(os.path.isdir(path)):
            os.makedirs(path)
        
    count = 0
    for idx in indices[0:month_delta+1]:
        month_val = dates[idx].month
        month = f'0{month_val}' if (month_val < 10) else month_val
        file_name = f'{dates[idx].year}_{month}.npy'
        np.save(os.path.join(UP_PRE, file_name), u_pre_training[count])
        np.save(os.path.join(NET_PRE, file_name), n_pre_training[count])
        np.save(os.path.join(DOWN_PRE, file_name), d_pre_training[count])
        count+=1

    count = 0
    print(indices)
    for idx in indices[month_delta:]:
        month_val = dates[idx].month
        month = f'0{month_val}' if (month_val < 10) else month_val
        file_name = f'{dates[idx].year}_{month}.npy'
        np.save(os.path.join(UP_POST, file_name), u_post_training[count])
        np.save(os.path.join(NET_POST, file_name), n_post_training[count])
        np.save(os.path.join(DOWN_POST, file_name), d_post_training[count])
        count+=1