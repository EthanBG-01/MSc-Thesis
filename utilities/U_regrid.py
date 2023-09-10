import U_config as cfg
import H_grid_set as gs
import cartopy.crs as ccrs

class regrid():

    def __init__(self, lats, lons):
        m = ccrs.NorthPolarStereo()
        G1 = gs.grid_set(m)
        G1.set_grid_lon_lat(lons, lats, fill_lonlat=True)    
        G2 = gs.grid_set(m)
        G2.load_grid(cfg.THICKNESS_GRID)
        G1tG2 = gs.Gs2Gs(G1, G2)
        self.regrid_object = G1tG2

    #def __init__(self, grid_path):
    #    m = ccrs.NorthPolarStereo()
    #    G1 = gs.grid_set(m)
    #    G1.load_grid(grid_path)
    #    G2 = gs.grid_set(m)
    #    G2.load_grid(cfg.THICKNESS_GRID)
    #    G1tG2 = gs.Gs2Gs(G1, G2)
    #    self.regrid_object = G1tG2

    def perform_regridding(self, data):
        return self.regrid_object.rg_array(data)