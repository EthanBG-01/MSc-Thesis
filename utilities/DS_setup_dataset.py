import os
import glob
import sys
import numpy as np
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
import U_config as cfg
from scipy import interpolate

sit_mask = "./arctic_hole_masks/thickness_mask.npy"
both_vars = {"sea_surface_temperature":cfg.ERA5_PROCESSED, "2m_temperature":cfg.ERA5_PROCESSED, "mean_sea_level_pressure":cfg.ERA5_PROCESSED, "geopotential":cfg.ERA5_PROCESSED, "surface_net_solar_radiation":cfg.ERA5_PROCESSED, "surface_solar_radiation_upwards":cfg.ERA5_PROCESSED, "surface_solar_radiation_downwards":cfg.ERA5_PROCESSED, "10m_u_component_of_wind":cfg.ERA5_PROCESSED, "10m_v_component_of_wind":cfg.ERA5_PROCESSED}
#post_only_vars = {"u_drift":cfg.SID_U_PROCESSED, "v_drift":cfg.SID_V_PROCESSED, "sit":cfg.SIT_PROCESSED}


def interpolate_polar_hole(sample_data, mask):
    mask = np.array(mask, dtype='bool')
    xx, yy = np.meshgrid(np.arange(104), np.arange(104))
    valid = ~mask
    x = xx[valid]
    y = yy[valid]
    x_interp = xx[mask]
    y_interp = yy[mask]
    values = sample_data[valid]
    interpolated_data = interpolate.griddata((x, y), values, (x_interp, y_interp), method='linear')
    sample_data[mask] = interpolated_data
    return sample_data

def normalise(data):
    data = np.array(data)
    min = np.nanmin(data)
    max = np.nanmax(data)
    return ((data - min)/ (max-min))

def standardise(data):
    data = np.array(data)
    mean = np.nanmean(data)
    sigma = np.nanstd(data)
    return ((data - mean)/ sigma)

if __name__ == '__main__':
    standard = True

    for var in list(both_vars.keys()):
        print(f'Sorting data for {var}...')
        path = os.path.join(cfg.ERA5_PROCESSED, var) if (both_vars[var] == cfg.ERA5_PROCESSED) else both_vars[var]
        files = os.listdir(path)

        # ================ EXTRACTING PROCESSED DATA SAMPLES ================
        #pre_samples = []
        #for i in range(0, 384):
        #    pre_samples.append(np.load(os.path.join(path, files[i])))

        post_samples = []
        for i in range(372, len(files)):
            post_samples.append(np.load(os.path.join(path, files[i])))

        # pre_samples = np.array(pre_samples)
        post_samples = np.array(post_samples)
  
        print(f'\nNormalising/ standardising data for {var}.') 
        if var in ["surface_net_solar_radiation", "surface_solar_radiation_downwards"]:
        #    pre_samples = pre_samples / (60*60*24)
            post_samples = post_samples / (60*60*24)

        if (var != "sic"):
        #    pre_samples = standardise(pre_samples) if (standard) else normalise(pre_samples) 
            post_samples = standardise(post_samples) if (standard) else normalise(post_samples) 
            
        #pre_save_loc = os.path.join(cfg.DATASET_FOLDER, 'pre_standard', var)
        #if not(os.path.isdir(pre_save_loc)):
        #    os.makedirs(pre_save_loc)

        post_save_loc = os.path.join(cfg.DATASET_FOLDER, 'post_standard', var)
        if not(os.path.isdir(post_save_loc)):
            os.makedirs(post_save_loc)

        if (var == "sic"):
            pass
            #mask_file = np.load("./arctic_hole_masks/polar_hole_87.npy") 
            #for i in range(0, 384):
            #    if (i==104): 
            #        mask_file = np.load("./arctic_hole_masks/polar_hole_2007.npy")
            #    if (i==348):
            #        mask_file = np.load("./arctic_hole_masks/polar_hole_present.npy")

            #    data = pre_samples[i]
            #    y = np.zeros((100,4))
            #    x = np.zeros((4, 104))
            #    data = np.append(data, y, axis=1)
            #    data = np.append(data, x, axis=0)
            #   data = interpolate_polar_hole(data, mask_file)
            #    data[np.isnan(data)] = 0
            #    np.save(os.path.join(pre_save_loc, str(files[i])), data)

            #count = 0
            #mask_file = np.load("./arctic_hole_masks/polar_hole_present.npy")

            #for i in range(372, len(files)):
            #    data = post_samples[count]
            #   y = np.zeros((100,4))
            #    x = np.zeros((4, 104))
            #    data = np.append(data, y, axis=1)
            #   data = np.append(data, x, axis=0)
            #    data = interpolate_polar_hole(data, mask_file)
            #    data[np.isnan(data)] = 0
            #    np.save(os.path.join(post_save_loc, str(files[i])), data)
            #    count += 1
        else: 
            #for i in range(0, 384):
            #    data = pre_samples[i]
            #    y = np.zeros((100,4))
            #    x = np.zeros((4, 104))
            #    data = np.append(data, y, axis=1)
            #    data = np.append(data, x, axis=0)
            #    data[np.isnan(data)] = 0
            #    np.save(os.path.join(pre_save_loc, str(files[i])), data)
            
            count = 0
            for i in range(372, len(files)):
                data = post_samples[count]
                y = np.zeros((100,4))
                x = np.zeros((4, 104))
                data = np.append(data, y, axis=1)
                data = np.append(data, x, axis=0)
                data[np.isnan(data)] = 0
                print(f"Saving to {post_save_loc}")
                np.save(os.path.join(post_save_loc, str(files[i])), data)
                count+=1

    raise Exception("NO")

    for var in list(post_only_vars.keys()):
        print(f'Sorting data for {var}...')
        path = post_only_vars[var]
        files = os.listdir(path)

        samples = []
        for i in range(0, len(files)):
            samples.append(np.load(os.path.join(path, files[i])))
        
        samples = np.array(samples)
  
        print(f'\nNormalising/ standardising data for {var}.')   
        samples = standardise(samples) if (standardise) else normalise(samples) 
            
        post_save_loc = os.path.join(cfg.DATASET_FOLDER, 'post_standard', var)
        if not(os.path.isdir(post_save_loc)):
            os.makedirs(post_save_loc)

        if (var == "sit"):
            mask_file = np.load("./arctic_hole_masks/thickness_mask.npy") 
            for i in range(0, len(samples)):
                data = samples[i]
                data = interpolate_polar_hole(data, mask_file)
                y = np.zeros((100,4))
                x = np.zeros((4, 104))
                data = np.append(data, y, axis=1)
                data = np.append(data, x, axis=0)
                data[np.isnan(data)] = 0
                np.save(os.path.join(post_save_loc, str(files[i])), data)
        else:
             for i in range(0, len(samples)):
                data = samples[i]
                y = np.zeros((100,4))
                x = np.zeros((4, 104))
                data = np.append(data, y, axis=1)
                data = np.append(data, x, axis=0)
                data[np.isnan(data)] = 0
                np.save(os.path.join(post_save_loc, str(files[i])), data)