import pandas as pd
import tensorflow as tf
import datetime
import numpy as np
import os
import random
from dateutil.relativedelta import relativedelta

"""
THIS FILE IS A COPY OF DATA_LOADER, BUT ENABLES A VARIABLE TO BE WEIGHTED AS ZERO THROUGH 'PREMUTE_VAR'.
"""

class ThesisDataLoader(tf.keras.utils.Sequence):
    
    def __init__(self, dataset_config):
        
        print(f'Initializing data loader...')
        self.SAMPLE_SHAPE = (104, 104)
        self.DATA_FOLDER = os.path.join(os.path.dirname(os.getcwd()), 'data', "datasets", dataset_config["data_path"])
        self.VARS = dataset_config["variables"]    
        self.LEAD_TIME = dataset_config["lead_time"]
        self.BATCH_SIZE = dataset_config["batch_size"]
        self.PERMUTE_VAR = dataset_config["permute_var"]
    
        # =========== DETERMINE DATE RANGE =============
        self.dates = list(pd.date_range(start=dataset_config["forecast_start"], end=dataset_config["forecast_end"], freq='MS'))
        #self.premute_dates = list(pd.date_range(start=dataset_config["forecast_start"], end=dataset_config["forecast_end"], freq='MS')).shuffle()
        print(f'Dataloader range: {self.dates[0]} to {self.dates[-1]}.')
        print(self.dates)

        # =========== VARIABLE SOURCES  =============
        self.VARIABLE_PATHS = {}
        for var in list(self.VARS.keys()):
            self.VARIABLE_PATHS[var] = os.path.join(self.DATA_FOLDER, var, '{0:4d}_{month}.npy')
            print(f"{self.VARIABLE_PATHS[var]}")
            
        self.GROUND_TRUTH_MASK = os.path.join(self.DATA_FOLDER, "sic", '{0:4d}_{month}.npy')
        
        # Ensure the start date is late enough for the selected variables to be used.
        max_lag = max(list(dataset_config["variables"].values()))
        earliest_date = self.dates[0] - relativedelta(months = max_lag)
        if (earliest_date < datetime.datetime(1979, 1, 1)):
            raise Exception("Forecast start date not feasible, with available data.")
        
        self.TOTAL_CHANNELS = sum(list(dataset_config["variables"].values()))
        return

    def __getitem__(self, batch_num):
        batch_start = batch_num * self.BATCH_SIZE
        batch_end = min((batch_num+1)*self.BATCH_SIZE, len(self.dates))
        samples = np.arange(batch_start, batch_end)
        batch_IDs = [self.dates[sample] for sample in samples]
        return self.get_samples(batch_IDs)

    def __len__(self):
        return int(np.ceil(len(self.dates) / self.BATCH_SIZE))

    def get_samples(self, date_list):
        X = np.zeros((len(date_list), *self.SAMPLE_SHAPE, self.TOTAL_CHANNELS), dtype=np.float32)
        y = np.zeros((len(date_list), *self.SAMPLE_SHAPE, 1), dtype=np.float32)

        for ID, date in enumerate(date_list):

            # Forecasting from this date:
            # E.g. if the date is 1980-01-01, with 1 month LEAD TIME, this becomes 1979-12-01
            # Relative lags are calculated back from this.
            forecast_origin = date - relativedelta(months = self.LEAD_TIME)

            # Get the ground truth for that DATE:
            month_inp = f'0{str(date.month)}' if (date.month < 10) else str(date.month)
            y[ID, :, :, 0:1] = np.stack([np.load(self.GROUND_TRUTH_MASK.format(date.year, month=month_inp))], axis=-1)            
            
            # Get the data for all the variables:
            channels = 0
            for var in self.VARS:
                for lag in range(0, self.VARS[var]):
                    if var == self.PERMUTE_VAR:
                        print("PERMUTE IMPORTANCE")
                        X[ID, :, :, channels:channels+1] = np.stack([np.zeros((104, 104))], axis=-1)   
                        print(X[ID, :, :, channels:channels+1])
                    else:
                        path = self.VARIABLE_PATHS[var]
                        sample_date = forecast_origin - relativedelta(months = lag)            
                        sample_yr = sample_date.year
                        sample_month = f'0{sample_date.month}' if (sample_date.month < 10) else sample_date.month
                        X[ID, :, :, channels:channels+1] = np.stack([np.load(path.format(sample_yr, month=sample_month))], axis=-1)   
                    channels+=1
        return X, y