import os
import sys
import datetime as dt
from dateutil.relativedelta import relativedelta
import numpy as np
from scipy import interpolate
import cartopy.crs as ccrs

import U_regrid as rg
import U_config as cfg

# Harry's Code:
import H_data_handler
import H_dates_weights

if __name__ == '__main__':
    var = str(sys.argv[1])

    if (var != 'DRIFT'):

        if (var == "SIC"):
            print(f'Processing NSIDC SIC data...')
            start_date = dt.datetime(cfg.SIC_START_YEAR,1,1)
            end_date = dt.datetime(cfg.SIC_END_YEAR,12,1)
            
            N = H_data_handler.NSIDC_nt(cfg.SIC_RAW, monthly=True)
            N.get_dates(start_date, end_date)
            print(f'Found {len(N.dates)} dates.')
            SIC = N.get_aice(N.dates)

            print(f'Regriddding data...')
            regridder = rg.regrid(cfg.NSIDC_GRID)
            samples = []
            for sample in range(0, len(N.dates)):
                samples.append(regridder.perform_regridding(SIC[sample]))

            print(f'Saving monthly SIC data...')
            if not(os.path.isdir(cfg.SIC_PROCESSED)):
                os.makedirs(cfg.SIC_PROCESSED)
            
            dir = cfg.SIC_PROCESSED
            dates_list = N.dates
        
        elif (var == "SIT"):
            print(f'Processing Cryosat SIT data...')
            # THIS IS THE MAXIMUM RANGE (AS OF NOW) - DON'T TOUCH
            start_date = dt.datetime(cfg.SIT_START_YEAR,10,1)
            end_date = dt.datetime(cfg.SIT_END_YEAR,7,1) 
            B = H_data_handler.Bristol_thickness_seasonal(cfg.SIT_RAW)
            B.get_dates(start_date, end_date)
            
            month_delta = (end_date.month - start_date.month) + (12*(end_date.year - start_date.year))
            dates_list  = [start_date + relativedelta(months = m) for m in range(0, month_delta+1)]   

            samples = []
            for i in range(0, month_delta):
                time_u = dates_list[i]
                time_w = relativedelta(months=1)
                dates_L = H_dates_weights.select_dates(B.dates,time_u,time_w)
                load_W =  H_dates_weights.get_load_points(dates_L,time_u,time_w)
                hi_L = B.get_hi(dates_L)
                hi = np.nansum(hi_L*load_W[:,None,None],axis=0)
                samples.append(hi)
            
            print(f'Saving monthly SIT data...')
            if not(os.path.isdir(cfg.SIT_PROCESSED)):
                os.makedirs(cfg.SIT_PROCESSED)
            dir = cfg.SIT_PROCESSED

        count = 0
        for sample in samples:
            month_val = dates_list[count].month
            month = f'0{month_val}' if (month_val < 10) else month_val
            file_name = f'{dates_list[count].year}_{month}.npy'
            save_loc = os.path.join(dir, file_name)
            np.save(save_loc, samples[count])
            count+=1

    elif (var == "DRIFT"):

        P = H_data_handler.Pathfinder_weekly(cfg.SID_RAW)
        start_date = dt.datetime(cfg.SID_START_YEAR,1,1)
        end_date = dt.datetime(cfg.SID_END_YEAR,1,1) 
        P.get_dates(start_date, end_date)
       
        month_delta = (end_date.month - start_date.month) + (12*(end_date.year - start_date.year))
        dates_list  = [start_date + relativedelta(months = m) for m in range(0, month_delta+1)]   

        u_samples = []
        v_samples = []
        for i in range(0, month_delta):
            time_u = dates_list[i]
            time_w = relativedelta(months=1)
            dates_L = H_dates_weights.select_dates(P.dates,time_u,time_w)
            load_W =  H_dates_weights.get_load_points(dates_L,time_u,time_w)
            u_L, v_L = P.get_vels(dates_L)
            u = np.nansum(u_L*load_W[:,None,None],axis=0)
            v = np.nansum(v_L*load_W[:,None,None],axis=0)
            u_samples.append(u)
            v_samples.append(v)

        if not(os.path.isdir(cfg.SID_U_PROCESSED)):
            os.makedirs(cfg.SID_U_PROCESSED)

        if not(os.path.isdir(cfg.SID_V_PROCESSED)):
            os.makedirs(cfg.SID_V_PROCESSED)

        print(f'Regriddding data...')
        regridder = rg.regrid(cfg.DRIFT_GRID)

        for sample in range(0, len(dates_list)-1):
            month_val = dates_list[sample].month
            month = f'0{month_val}' if (month_val < 10) else month_val
            file_name = f'{dates_list[sample].year}_{month}.npy'
            
            # Save the U and V components of drift:
            u_save_loc = os.path.join(cfg.SID_U_PROCESSED, file_name)
            v_save_loc = os.path.join(cfg.SID_V_PROCESSED, file_name)
            u_rg = regridder.perform_regridding(u_samples[sample])
            v_rg = regridder.perform_regridding(v_samples[sample])
            np.save(u_save_loc, u_rg)
            np.save(v_save_loc, v_rg)
