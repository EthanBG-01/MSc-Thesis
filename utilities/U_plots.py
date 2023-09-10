import numpy as np
import os

import matplotlib.pyplot as plt

import cartopy.feature as cfeature
import cartopy.crs as ccrs
import U_regrid as rg
import U_config as cfg
import H_grid_set as gs

m = ccrs.NorthPolarStereo()
GRID = gs.grid_set(m)
GRID.load_grid(os.path.join(os.path.dirname(os.getcwd()), 'utilities', 'grids', 'Thickness_Grid.npz'))

f = plt.figure()
ax = f.add_subplot(1,1,1,projection=m)
ax.set_extent([-180, 180, 65, 90], ccrs.PlateCarree())
Gplot = gs.grid_set(m)
Gplot.set_grid_mn(30, 30,ax) 
Gplot.gridinfo = False
Gplot.get_grid_info(av_ang=False)
GP2Gplot= gs.Gs2Gs(GRID,Gplot,vectors=True)
f.clear()

class plots:
    def __init__(self):
        return
    

    def plot_single_var(self, data, title, cmap_selection, label, vmin, vmax, contour=True):
        f = plt.figure(figsize=[8,8])
        ax = f.add_subplot(1,1,1,projection=m)
        ax.set_extent([-180, 180, 65, 90], ccrs.PlateCarree())
        cmap = plt.cm.get_cmap(cmap_selection).reversed()

        if contour:
            s=ax.contourf(GRID.xptp, GRID.yptp, data, 25, cmap=cmap)
        else:
            s = ax.pcolormesh(GRID.xptp, GRID.yptp, data, vmin=vmin, vmax=vmax, cmap=cmap)
        
        ax.set_title(f'{title}')
        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.COASTLINE)
        ax.gridlines(draw_labels=False)
        cbar = plt.colorbar(s, shrink=0.8,pad=0.05)
        cbar.set_label(f'{label}', fontsize=12)
        plt.show()

    # SIC AS PERCENTAGES!
    def plot_comparison(self, truth, prediction_A, prediction_B, date, save_loc, min, max, contour=True):
        fig, axes = plt.subplots(1,3, figsize=(12, 4), constrained_layout=True, subplot_kw={"projection": ccrs.NorthPolarStereo()})
        fig.suptitle(f'NSIDC and Network Prediction for {date}', fontsize=12)
        map=plt.cm.get_cmap('Spectral').reversed()

        titles = ["NSIDC SIC %", "Observational Thickness & Drift\nSIC %", "Baseline\nSIC %"]
        
        plots= [truth, prediction_A, prediction_B]

        p=0
        for ax in axes.flat:
            ax.set_extent([-180, 180, 65, 90], ccrs.PlateCarree())
            ax.set_title(titles[p], fontsize=9)
            ax.add_feature(cfeature.LAND)
            ax.add_feature(cfeature.COASTLINE)
            ax.gridlines(draw_labels=False)    
            if contour:
                s=ax.contourf(GRID.xptp, GRID.yptp, plots[p], np.linspace(0, 100, 10), cmap=map)
            else:
                s=ax.pcolormesh(GRID.xptp, GRID.yptp, plots[p], vmin=min, vmax=max, cmap=map)
            p+=1

        cbar = fig.colorbar(s, ax=axes.ravel().tolist(), location='bottom', shrink=0.4, pad=0.02)

        for t in cbar.ax.get_yticklabels():
            t.set_fontsize(8)

        plt.savefig(save_loc)
        plt.show()

    def plot_anomaly(self, truth, prediction_A, prediction_B, date, save_loc, contour=True):
   
        prediction_A_anom = prediction_A - truth
        prediction_B_anom = prediction_B - truth
    
        fig, (ax1, ax2, ax3) = plt.subplots(1,3, figsize=(12, 4), constrained_layout=True, subplot_kw={"projection": ccrs.NorthPolarStereo()})
        fig.suptitle(f'NSIDC and Network Prediction Anommalies for {date}', fontsize=12)

        axs = [ax1, ax2, ax3]
        ax1.set_title("NSIDC Observational Sea Ice Concentration (SIC)", fontsize=9)
        ax2.set_title("Thickness & Drift Included\nSIC Anomaly %", fontsize=9)
        ax3.set_title("Re-Analysis Only\nSIC Anomaly %", fontsize=9)

        for ax in axs:
            ax.set_extent([-180, 180, 65, 90], ccrs.PlateCarree())
        
        # For the ice:
        map=plt.cm.get_cmap('Blues').reversed()
        map.set_bad('black',np.nan)

        if contour:
            s1=ax1.contourf(GRID.xptp, GRID.yptp, truth*100, 10, cmap=map)
            s2=ax2.contourf(GRID.xptp, GRID.yptp, prediction_A_anom*100, np.linspace(-40, 40, 10), cmap="RdBu")
            s3=ax3.contourf(GRID.xptp, GRID.yptp, prediction_B_anom*100, np.linspace(-40, 40, 10), cmap="RdBu")
        else:
            s1=ax1.pcolormesh(GRID.xptp, GRID.yptp, truth*100, cmap=map)
            s2=ax2.pcolormesh(GRID.xptp, GRID.yptp, prediction_A_anom*100, vmin=-40, vmax=40, cmap="RdBu")
            s3=ax3.pcolormesh(GRID.xptp, GRID.yptp, prediction_B_anom*100, vmin=-40, vmax=40, cmap="RdBu")
        
        for ax in axs:
            ax.add_feature(cfeature.LAND)
            ax.add_feature(cfeature.COASTLINE)
            ax.gridlines(draw_labels=False)    
        
        cbars = []
        cbar1 = plt.colorbar(s1, ax=ax1, shrink=0.98, pad=0.05)
        cbar3 = plt.colorbar(s3, ax=ax3, shrink=0.98, pad=0.05)
        cbar1.set_label("SIC in %", fontsize=9)
        cbar3.set_label("Anomaly in %", fontsize=9)
        cbars.append(cbar1)
        cbars.append(cbar3)
        
        for cbar in cbars:
            for t in cbar.ax.get_yticklabels():
                t.set_fontsize(7)

        plt.savefig(save_loc)
        plt.show()

    def plot_grouped_anomaly(self, truth, prediction_A, prediction_B, date, save_loc, contour=True):
   
        prediction_A_anom = prediction_A - truth
        prediction_B_anom = prediction_B - truth
    
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4), constrained_layout=True, subplot_kw={"projection": ccrs.NorthPolarStereo()})
        fig.suptitle(f'NSIDC and Network Prediction Anommalies for {date}', fontsize=12)

        axs = [ax1, ax2]
        ax1.set_title("Thickness & Drift Included\nSIC Anomaly %", fontsize=9)
        ax2.set_title("Re-Analysis Only\nSIC Anomaly %", fontsize=9)
        
        for ax in axs:
            ax.set_extent([-180, 180, 65, 90], ccrs.PlateCarree())
        
        # For the ice:
        map=plt.cm.get_cmap('Blues').reversed()
        map.set_bad('black',np.nan)

        if contour:
            s1=ax1.contourf(GRID.xptp, GRID.yptp, prediction_B_anom, np.linspace(-0.4, 0.4, 10), cmap="RdBu")
            s2=ax2.contourf(GRID.xptp, GRID.yptp, prediction_A_anom, np.linspace(-0.4, 0.4, 10), cmap="RdBu")
        else:
            s1=ax1.pcolormesh(GRID.xptp, GRID.yptp, prediction_B_anom, vmin=-0.4, vmax=0.4, cmap="RdBu")
            s2=ax2.pcolormesh(GRID.xptp, GRID.yptp, prediction_A_anom, vmin=-0.4, vmax=0.4, cmap="RdBu")
            
        for ax in axs:
            ax.add_feature(cfeature.LAND)
            ax.add_feature(cfeature.COASTLINE)
            ax.gridlines(draw_labels=False)    
        
        cbar = plt.colorbar(s1, ax=ax2, shrink=0.68, pad=0.05)
        cbar.set_label("Anomaly in %", fontsize=9)
        
        for t in cbar.ax.get_yticklabels():
            t.set_fontsize(7)

        cbar.ax.set_yticks(np.arange(-0.4, 0.4, 0.1))

        plt.savefig(save_loc)
        plt.show()

    def plot_prediction(self, truth, prediction_A, prediction_B, date, saveloc, contour=True):

        fig, (ax1, ax2, ax3) = plt.subplots(1,3, figsize=(12, 4), constrained_layout=True, subplot_kw={"projection": ccrs.NorthPolarStereo()})
        fig.suptitle(f'NSIDC and Model Predicted Sea Ice Concentration for {date}', fontsize=12)

        axs = [ax1, ax2, ax3]
        ax1.set_title("NSIDC SIC %", fontsize=10)
        ax2.set_title("Observational Thickness & Drift\nSea Ice Concentration", fontsize=10)
        ax3.set_title("Baseline\nSea Ice Concentration", fontsize=10)

        for ax in axs:
            ax.set_extent([-180, 180, 65, 90], ccrs.PlateCarree())
        
        # For the ice:
        map=plt.cm.get_cmap('Blues').reversed()
        map.set_bad('black',np.nan)

        if contour:
            s1=ax1.contourf(GRID.xptp, GRID.yptp, truth, np.linspace(0, 100, 10), cmap=map)
            s2=ax2.contourf(GRID.xptp, GRID.yptp, prediction_A, np.linspace(0, 100, 10), cmap=map)
            s3=ax3.contourf(GRID.xptp, GRID.yptp, prediction_B, np.linspace(0, 100, 10), cmap=map)
        else:
            s1=ax1.pcolormesh(GRID.xptp, GRID.yptp, truth, vmin=0, vmax=100, cmap=map)
            s2=ax2.pcolormesh(GRID.xptp, GRID.yptp, prediction_A, vmin=0, vmax=100, cmap=map)
            s3=ax3.pcolormesh(GRID.xptp, GRID.yptp, prediction_B, vmin=0, vmax=100, cmap=map)
        
        for ax in axs:
            ax.add_feature(cfeature.LAND)
            ax.add_feature(cfeature.COASTLINE)
            ax.gridlines(draw_labels=False)    
        
        cbar = plt.colorbar(s3, ax=ax3, shrink=0.99, pad=0.05)
        cbar.set_label("SIC in %", fontsize=9)
        
        for t in cbar.ax.get_yticklabels():
            t.set_fontsize(7)
        plt.savefig(saveloc)
        plt.show()
    

    def plot_anom(self, truth, prediction_A, prediction_B, date, saveloc, col, contour=True):

        # NSIDC A-Anom B-Anom
        prediction_A_anom = prediction_A - truth
        prediction_B_anom = prediction_B - truth
    
        fig, (ax1, ax2, ax3) = plt.subplots(1,3, figsize=(12, 4), constrained_layout=True, subplot_kw={"projection": ccrs.NorthPolarStereo()})
        fig.suptitle(f'NSIDC and Model Prediction Anomalies for {date}', fontsize=12)

        axs = [ax1, ax2, ax3]
        ax1.set_title("NSIDC SIC %", fontsize=9)
        ax2.set_title("Thickness & Drift Included\nSIC Anomaly %", fontsize=9)
        ax3.set_title("Re-Analysis Only\nSIC Anomaly %", fontsize=9)

        for ax in axs:
            ax.set_extent([-180, 180, 65, 90], ccrs.PlateCarree())
        
        # For the ice:
        map=plt.cm.get_cmap('Blues').reversed()
        map.set_bad('black',np.nan)

        real_ice = np.zeros((100, 100))
        real_ice[np.where(truth>15)] = 1

        if contour:
            s1=ax1.contourf(GRID.xptp, GRID.yptp, truth, np.linspace(0, 100, 10), cmap=map)
            s2=ax2.contourf(GRID.xptp, GRID.yptp, prediction_A_anom, np.linspace(-50, 50, 10), cmap="RdBu")
            s3=ax3.contourf(GRID.xptp, GRID.yptp, prediction_B_anom, np.linspace(-50, 50, 10), cmap="RdBu")
        else:
            s1=ax1.pcolormesh(GRID.xptp, GRID.yptp, truth, vmin=0, vmax=100, cmap=map)
            s2=ax2.pcolormesh(GRID.xptp, GRID.yptp, prediction_A_anom, vmin=-60, vmax=60, cmap="RdBu")
            s3=ax3.pcolormesh(GRID.xptp, GRID.yptp, prediction_B_anom, vmin=-60, vmax=60, cmap="RdBu")

        NSIDC_extent_1 = ax2.contour(GRID.xptp, GRID.yptp, real_ice, 0, colors=col, linewidths=1.2)
        NSIDC_extent_2 = ax3.contour(GRID.xptp, GRID.yptp, real_ice, 0, colors=col, linewidths=1.2)

        count = 0
        for ax in axs:
            ax.add_feature(cfeature.LAND)
            ax.add_feature(cfeature.COASTLINE)
            if (count==0): ax.gridlines(draw_labels=False)    
            count+=1

        NSIDC_lab_1,_ = NSIDC_extent_2.legend_elements()
        ax.legend([NSIDC_lab_1[0]], ['NSIDC Sea Ice Extent'], loc="lower left", borderaxespad=0.2)

        cbars = []
        cbar1 = plt.colorbar(s1, ax=ax1, shrink=0.99, pad=0.05)
        cbar3 = plt.colorbar(s3, ax=ax3, shrink=0.99, pad=0.05)
        cbar1.set_label("SIC in %", fontsize=9)
        cbar3.set_label("Anomaly in %", fontsize=9)
        cbars.append(cbar1)
        cbars.append(cbar3)
        
        plt.savefig(saveloc)
        plt.show()

    def plot_anom_thick(self, truth, prediction_A, prediction_B, thickness, month, date, min, max, delta, saveloc, col, contour=True):

        # NSIDC A-Anom B-Anom
        prediction_A_anom = prediction_A - truth
        prediction_B_anom = prediction_B - truth
    
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2, figsize=(8, 8), constrained_layout=True, subplot_kw={"projection": ccrs.NorthPolarStereo()})
        fig.suptitle(f'NSIDC and Model Prediction Anomalies for {date}', fontsize=12)

        axs = [ax1, ax2, ax3, ax4]
        ax1.set_title("NSIDC SIC %", fontsize=9)
        ax2.set_title(f"Thickness in {month}", fontsize=9)
        ax3.set_title("Thickness & Drift Included\nSIC Anomaly %", fontsize=9)
        ax4.set_title("Re-Analysis Only\nSIC Anomaly %", fontsize=9)

        for ax in axs:
            ax.set_extent([-180, 180, 65, 90], ccrs.PlateCarree())
        
        # For the ice:
        map=plt.cm.get_cmap('Blues').reversed()
        map.set_bad('black',np.nan)

        real_ice = np.zeros((100, 100))
        real_ice[np.where(truth>15)] = 1

        if contour:
            s1=ax1.contourf(GRID.xptp, GRID.yptp, truth, np.linspace(0, 100, 10), cmap=map)
            map=plt.cm.get_cmap('Spectral').reversed()
            
            s1=ax2.contourf(GRID.xptp, GRID.yptp, thickness, np.linspace(min, max, delta), cmap=map)
            ax3.contourf(GRID.xptp, GRID.yptp, prediction_A_anom, np.linspace(-60, 60, 10), cmap="RdBu")
            s4=ax4.contourf(GRID.xptp, GRID.yptp, prediction_B_anom, np.linspace(-60, 60, 10), cmap="RdBu")
        else:
            s1=ax1.pcolormesh(GRID.xptp, GRID.yptp, truth, vmin=0, vmax=100, cmap=map)
            map=plt.cm.get_cmap('Spectral').reversed()
            
            s2=ax2.pcolormesh(GRID.xptp, GRID.yptp, thickness, vmin=min, vmax=max, cmap=map)
            ax3.pcolormesh(GRID.xptp, GRID.yptp, prediction_A_anom, vmin=-60, vmax=60, cmap="RdBu")
            s4=ax4.pcolormesh(GRID.xptp, GRID.yptp, prediction_B_anom, vmin=-60, vmax=60, cmap="RdBu")

        NSIDC_extent_1 = ax3.contour(GRID.xptp, GRID.yptp, real_ice, 0, colors=col, linewidths=1.2)
        NSIDC_extent_2 = ax4.contour(GRID.xptp, GRID.yptp, real_ice, 0, colors=col, linewidths=1.2)

        count = 0
        for ax in axs:
            ax.add_feature(cfeature.LAND)
            ax.add_feature(cfeature.COASTLINE)
            if (count==0 or count==1): ax.gridlines(draw_labels=False)    
            count+=1

        NSIDC_lab_1,_ = NSIDC_extent_2.legend_elements()
        ax4.legend([NSIDC_lab_1[0]], ['NSIDC Sea Ice Extent'], loc="lower left", borderaxespad=0.2)

        cbars = []
        cbar1 = plt.colorbar(s1, ax=ax1, shrink=0.8, pad=0.05)
        cbar2 = plt.colorbar(s2, ax=ax2, shrink=0.8, pad=0.05)
        cbar4 = plt.colorbar(s4, ax=ax4, shrink=0.8, pad=0.05)
        cbar1.set_label("SIC in %", fontsize=9)
        cbar2.set_label("Thickness in m", fontsize=9)
        cbar4.set_label("Anomaly in %", fontsize=9)
    
        
        plt.savefig(saveloc)
        plt.show()

    def plot_contours(self, NSIDC, baseline, observation, month, lead):
        f = plt.figure(figsize=[8,8])
        ax = f.add_subplot(1,1,1,projection=m)
        ax.set_extent([-180, 180, 65, 90], ccrs.PlateCarree())

        # 1 Month Lead:
        nsidc_ice = np.zeros((100, 100))
        nsidc_ice[np.where(NSIDC>0.15)] = 1

        base_ice = np.zeros((100, 100))
        base_ice[np.where(baseline>0.15)] = 1

        thick_ice = np.zeros((100, 100))
        thick_ice[np.where(observation>0.15)] = 1

        NSIDC_extent = ax.contour(GRID.xptp, GRID.yptp, nsidc_ice, 0, colors='#5c5c5c', linewidths=1.2)
        Thickness_extent = ax.contour(GRID.xptp, GRID.yptp, thick_ice, 0, colors='red', linewidths=1.5)
        Baseline_extent = ax.contour(GRID.xptp, GRID.yptp, base_ice,  0, colors='blue', linewidths=1.5, linestyles='dashed')

        NSIDC_lab,_ = NSIDC_extent.legend_elements()
        Thick_lab,_ = Thickness_extent.legend_elements()
        Baseline_lab,_ = Baseline_extent.legend_elements()

        ax.legend([NSIDC_lab[0], Thick_lab[0], Baseline_lab[0]], ['NSIDC', 'Observational Model', 'Baseline Model'])

        ax.set_title(f'{month} Sea Ice Extent ({lead} Month Lead Time)', fontsize=14, pad=10)
        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.COASTLINE)
        plt.savefig(f"../model/models/20/comparative/{month}_extent.png")
        plt.show()


    def plot_uncertainty(self, truth, prediction_A, prediction_B, date, save_loc, min, max, colour_map, title1, title2, contour=True):
    
        fig, axes = plt.subplots(1,3, figsize=(12, 4), constrained_layout=True, subplot_kw={"projection": ccrs.NorthPolarStereo()})
        fig.suptitle(f'{type} uncertainty {date}', fontsize=12)
    
        titles = ["NSIDC SIC %", title1, title2]
        
        plots= [truth, prediction_A, prediction_B]

        p=0
        cbars = []
        for ax in axes.flat:            
            ax.set_extent([-180, 180, 65, 90], ccrs.PlateCarree())
            ax.set_title(titles[p], fontsize=9)
            ax.add_feature(cfeature.LAND)
            ax.add_feature(cfeature.COASTLINE)
            ax.gridlines(draw_labels=False)    
            
            if p == 0:
               map=plt.cm.get_cmap('Blues').reversed()  
            else:
               map=plt.cm.get_cmap(colour_map).reversed()
            
            if contour:
                s=ax.contourf(GRID.xptp, GRID.yptp, plots[p], 10, cmap=map)
            else:
                s=ax.pcolormesh(GRID.xptp, GRID.yptp, plots[p], vmin=min, vmax=max, cmap=map)
            
            if p == 0:
                cbar = plt.colorbar(s, ax=ax, shrink=0.98, pad=0.05)
                cbar.set_label(titles[p])
                cbars.append(cbar)
            elif p == 2:
                cbar = plt.colorbar(s, ax=ax, shrink=0.98, pad=0.05)
                cbar.set_label(titles[p])
                cbars.append(cbar)
            p+=1
        
        for cbar in cbars:
            for t in cbar.ax.get_yticklabels():
                t.set_fontsize(8)

        plt.savefig(save_loc)
        plt.show()

        
   