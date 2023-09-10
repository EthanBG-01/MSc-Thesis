import numpy as np
import glob
import datetime as dt
from dateutil.relativedelta import relativedelta
import H_grid_set as gs
from netCDF4 import Dataset
import os

class NSIDC_nt():

    def __init__(self,ppath,monthly = False):
        self.name = 'NSIDC_n'
        self.path = ppath
        self.monthly = monthly 

    def get_aice(self,dates_u,verbos=False):
        dimY = 304
        dimX = 448
        d_no = np.shape(dates_u)[0]
        data =  np.empty([d_no, dimX, dimY])
        for n,d in enumerate(dates_u):

            if self.monthly:
                infile = os.path.join(self.path,"nt_"+d.strftime('%Y%m')+"_*.bin")
            else:
                infile = os.path.join(self.path,d.strftime('/%Y/')+"nt_"+d.strftime('%Y%m%d')+"_*.bin")
            flist  = glob.glob(infile)
            if len(flist) > 0:
                infile = flist[0]
            with open(infile, 'rb') as fr:
                hdr = fr.read(300)
                ice = np.fromfile(fr, dtype=np.uint8)

            ice = ice.reshape(dimX,dimY)
            ice = np.flipud(ice)
            data[n] = ice / 250.
        data[data>1.0] = np.nan
        return data

    def get_dates(self,time_start,time_end):
        dates_u = []
        if self.monthly:
            nyrs = time_end.year-time_start.year
            m_no = (time_end.month-time_start.month) + nyrs*12 + 1
            for mn in range(m_no):
                d = time_start+ relativedelta(months = mn )
                infile = os.path.join(self.path,"nt_"+d.strftime('%Y%m')+"_*.bin")
                flist  = glob.glob(infile)
                if len(flist) > 0:
                    infile = flist[0]
                    dates_u.append(d+relativedelta(days=14))
        else:
            d_no = (time_end-time_start).days +3 
            for dn in range(d_no):
                d = time_start+ relativedelta(days = dn - 1)
                infile = os.path.join(self.path, d.strftime('/%Y/')+"nt_"+d.strftime('%Y%m%d')+"_*.bin")
                flist  = glob.glob(infile)
                if len(flist) > 0:
                    infile = flist[0]
                    dates_u.append(d)
        self.dates= dates_u
        print(self.name+' Found '+str(np.shape(dates_u)[0])+' dates')

class Bristol_thickness_seasonal:
    def __init__(self,ppath,var='Sea_Ice_Thickness'):
        """
        var is
        'Sea_Ice_Thickness'
        """
        self.name = 'Bristol_hi_seasonal'
        self.path = ppath        
        self.var = var

    def get_dates(self,time_start,time_end,fill_end_months=False):
        """
        use the Time variable, single file sothis allows for access later 
        """
        
        self.file = os.path.join(self.path, 'ubristol_cryosat2_seaicethickness_nh_80km_v1p7.nc')
        self.f_nc = Dataset(self.file)
        self.time_vec = self.f_nc.variables['Time'][:]
        self.dates = [dt.datetime(1,1,1)+relativedelta(days=t) for t in self.time_vec]
        self.dates = [t+relativedelta(years = -1) for t in self.dates]
        print(self.name+' Found '+str(np.shape(self.dates)[0])+' dates')

    def get_hi(self,dates_u,verbos=False):
        """
        use the self.dates to find the index of the time in question
        """
        ### find the indices
        idx = [np.argwhere(np.array([d == du for d  in self.dates] ))[0,0] 
                                             for du in dates_u]
        if verbos:
            for i,du in zip(idx,dates_u):
                dcheck = dt.datetime(1,1,1)
                dcheck = dcheck+relativedelta(days=self.time_vec[i])
                dcheck = dcheck+relativedelta(years=-1)
                print(du.strftime('%Y%m%d-')+dcheck.strftime('%Y%m%d'))
        hi = self.f_nc.variables[self.var][idx]
        return hi.data

    def get_err(self,dates_u,verbos=False):
        ## errs need to be dimensional
        """
        use the self.dates to find the index of the time in question
        """
        ### find the indices
        idx = [np.argwhere(np.array([d == du for d  in self.dates] ))[0,0] 
                                             for du in dates_u]
        if verbos:
            for i,du in zip(idx,dates_u):
                dcheck = dt.datetime(1,1,1)
                dcheck = dcheck+relativedelta(days=self.time_vec[i])
                dcheck = dcheck+relativedelta(years=-1)
                print(du.strftime('%Y%m%d-')+dcheck.strftime('%Y%m%d'))
        hi = self.f_nc.variables['Sea_Ice_Thickness_Uncertainty'][idx]
        return hi.data
    

class Pathfinder_weekly():
    """
    forcing class for the budget
    lets the forcing load efficiently
    
    """
    def __init__(self,ppath,hemi='north'):
        self.name = 'Pathfinder'
        self.path = ppath
        self.hemi = hemi
        self.vyear_load = 0
        self.vels_loaded = False
        
    def get_dates(self,time_start,time_end):
        """
        returns the all encompassing date list for use with the forcing object
        """
        dates =[]
        d0 = dt.datetime(1970,1,1)
        n_yrs = (time_end.year - time_start.year)+1
        for y in range(n_yrs):
            yu = time_start.year + y
            if self.hemi == 'north':
                #### icemotion_weekly_nh_25km_20140101_20141231_v4.1.nc
                f_name = 'icemotion_weekly_nh_25km_'+str(yu)+'0101_'+str(yu)+'1231_v4.1.nc'
            elif self.hemi == 'south':
                ### icemotion_weekly_sh_25km_20100101_20101231_v4.1.nc
                f_name = 'icemotion_weekly_sh_25km_'+str(yu)+'0101_'+str(yu)+'1231_v4.1.nc'
            if os.path.isfile(os.path.join(self.path,f_name)):
                f_nc = Dataset(os.path.join(self.path, f_name))
                [dates.append(d0 + relativedelta(days = d))
                     for d in f_nc['time'][:]]
                f_nc.close()
        self.dates = dates
        print(self.name+' Found '+str(np.shape(dates)[0])+' dates')

    # weekly points in yearly files

    # next function will take a list of dates and return an appropriately orientated arrays
    # give a 
    def get_vels(self,dates_u,verbos=False):
        d0 = dt.datetime(1970,1,1)
        # does dates_u cover one year or more
        year_append = False
        datau = []
        datav = []
        if (dates_u[-1].year -dates_u[0].year) > 0:
            year_append = True
            yuse = [dates_u[0].year,dates_u[-1].year]
        else:
            yuse = [dates_u[0].year]
        for yu in yuse: 
            if ((self.vyear_load != yu) or (not self.vels_loaded)):
                print('loading new year of data: '+str(yu))
                if self.hemi == 'north':
                    f_name = 'icemotion_weekly_nh_25km_'+str(yu)+'0101_'+str(yu)+'1231_v4.1.nc'
                elif self.hemi == 'south':
                    ### icemotion_weekly_sh_25km_20100101_20101231_v4.1.nc
                    f_name = 'icemotion_weekly_sh_25km_'+str(yu)+'0101_'+str(yu)+'1231_v4.1.nc'
#                 f_name = 'icemotion_weekly_nh_25km_'+str(yu)+'0101_'+str(yu)+'1231_v4.1.nc'
                f_nc = Dataset(os.path.join(self.path,f_name))
        #         print(p0,p1)
                self.u = f_nc['u'][:]
                self.v = f_nc['v'][:]
                self.u[self.u.mask] = np.nan
                self.v[self.v.mask] = np.nan
                #### also load time vec
                self.d_load = [d0 + relativedelta(days = d) for d in f_nc['time'][:]]
                f_nc.close()
                self.vyear_load = yu
                self.vels_loaded= True
            ### need indexes
            dates_u_yu = [d for d in dates_u if d.year == yu]
            idx = [np.argwhere(np.array([d == du for d  in self.d_load] ))[0,0] 
                                             for du in dates_u_yu]
            datau.append(self.u[idx,:,:].transpose((0,2,1))/100)
            datav.append(self.v[idx,:,:].transpose((0,2,1))/100)
        if year_append: 
            return np.vstack(datau),np.vstack(datav)
        else:
            return datau[0],datav[0]
        
