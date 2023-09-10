## Data Folders

- Ice-Related products were supplied by Harry Heorton, and simply copied into the relevant ice folders.
- ERA5 reanalysis was acquired using a Python script (utilities) that then produced `.nc4` files.
- Pre-processing converted files into monthly `.npy` samples, clearly labelled to faciliate future processing & use within Tensorflow.

```
./data
    ./datasets
        ./pre [1979->2010]
        ./post [2010 -> 2020]
    ./processed_data
        ./NSIDC
        ./thickness
        ./u_drift
        ./v_drift
        ./era5
    ./raw_data
        ./NSIDC
            |-nt_197811_n07_v1.1_n.bin
            |- ...
        ./thickness
            |-ubristol_cryosat2_seaicethickness_nh_80km_v1p7.nc
        ./drift
            |- ...
        ./era5
            |-2m_temperature_raw_data.nc4
            |-geopotential_raw_data.nc4
            |-mean_seal_level_pressure_raw_data.nc4
            |-sea_surface_temperature_raw_data.nc4
            |-surface_net_solar_radiation_raw_data.nc4
            |-surface_solar_radiation_downwards_raw_data.nc4
```
