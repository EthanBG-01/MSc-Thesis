import os

DATA_FOLDER = os.path.join(os.path.dirname(os.getcwd()), 'data')
DATASET_FOLDER = os.path.join(os.path.dirname(os.getcwd()), 'data','datasets')

# =========== ERA5 ===========
ERA5_RAW = os.path.join(DATA_FOLDER, 'raw_data', 'era5')
ERA5_PROCESSED = os.path.join(DATA_FOLDER, 'processed_data', 'era5')
ERA5_DS = os.path.join(DATASET_FOLDER, 'post', 'era5')

# =========== NSIDC ===========
SIC_RAW = os.path.join(DATA_FOLDER, 'raw_data', 'NSIDC', 'SIC')
SIC_PROCESSED = os.path.join(DATA_FOLDER, 'processed_data', 'sic')
SIC_START_YEAR = 1979
SIC_END_YEAR = 2022

# =========== THICKNESS ===========
SIT_RAW = os.path.join(DATA_FOLDER, 'raw_data', 'thickness')
SIT_PROCESSED = os.path.join(DATA_FOLDER, 'processed_data', 'sit')
SIT_START_YEAR = 2010
SIT_END_YEAR = 2020

# =========== DRIFT ===========
SID_RAW = os.path.join(DATA_FOLDER, 'raw_data', 'drift')
SID_U_PROCESSED = os.path.join(DATA_FOLDER, 'processed_data', 'u_drift')
SID_V_PROCESSED = os.path.join(DATA_FOLDER, 'processed_data', 'v_drift')
SID_START_YEAR = 2010
SID_END_YEAR = 2021

# =========== GRIDS ===========
DRIFT_GRID = os.path.join(os.getcwd(), 'grids', 'Pathfinder_gs.npz')
NSIDC_GRID = os.path.join(os.getcwd(), 'grids', 'NSIDC_gs.npz')
THICKNESS_GRID = os.path.join(os.getcwd(), 'grids', 'Thickness_Grid.npz')

# =========== MODEL EXPERIMENTS =========== 
RESULTS_FOLDER = os.path.join(os.path.dirname(os.getcwd()), 'results')
MODELS_FOLDER = os.path.join(os.path.dirname(os.getcwd()), 'model')
PLOTS_FOLDER = os.path.join(os.path.dirname(os.getcwd()), 'plots')