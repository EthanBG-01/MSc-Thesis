import json
import datetime
import os
import sys
sys.path.append("../../utilities")
import U_config as cfg

"""
Short file to generate data-loader configs over command-line.
Facilitates quicker experimentation, essentially filling in JSON objects.
"""

pre_train_config_details = \
                {'lead_time':0, 
                  'forecast_start':None,
                  'forecast_end':None,
                  'data_path':'pre_standard',
                  'variables' : {},
                  'batch_size':4,
                  'permute_variable':None
                  }

post_train_config_details = \
                {'lead_time':0, 
                  'forecast_start':None,
                  'forecast_end':None,
                  'data_path':'post_standard',
                  'variables' : {},
                  'batch_size':4,
                  'permute_variable':None
                  }

testing_config_details = \
                {'lead_time':0, 
                  'forecast_start':None,
                  'forecast_end':None,
                  'data_path':'post_standard',
                  'variables' : {},
                  'batch_size':4,
                  'permute_variable':None
                  }

possible_vars = ["2m_temperature", 
                 "sea_surface_temperature", 
                 "mean_sea_level_pressure", 
                 "surface_solar_radiation_upwards",
                 "surface_solar_radiation_downwards",
                 "surface_net_solar_radiation", 
                 "10m_u_component_of_wind", 
                 "10m_v_component_of_wind", 
                 "sic",
                 "sit",
                 "u_drift",
                 "v_drift"]

def input_details(file, type):
    valid_file = False
    while not valid_file:
        file['lead_time'] = int(input(f'\nLead time: '))
        
        # Determine dates:
        start_year = int((input("Start year: ")))
        start_month = int((input("Month (1, 2, 3 etc.): ")))
        end_year = int((input("End year: ")))
        end_month = int((input("Month (1, 2, 3 etc.): ")))
        start_date = datetime.date(start_year,start_month,1)
        end_date = datetime.date(end_year,end_month,1)
        file["forecast_start"] = str(start_date)
        file["forecast_end"] = str(end_date)
        
        print("For the variables, enter 0 to ignore it, or the numerical value of lag.")
        print("For instance: SIC: 3 would result in the previous 3 SIC values being used.")
        for var in possible_vars:
            lag =int(input(f'{var} :'))
            if (lag != 0):
                file['variables'][var] = lag
        
        batch = int((input("Batch size: ")))
        file['batch_size'] = batch
        print("FILE:")
        print(file)

        check = input(str("Are you satisfied with this configuration? (y/n) :"))
        if check == 'y': valid_file = True
        
    print('Saving file...')
    file_loc = os.path.join(experiment_path, f'{type}.json')
    with open(file_loc, 'w') as outfile:
        json.dump(file, outfile)

    if (type == "post_training"):
        print('\nGenerating baseline post training setup based on your previous file ...')
        file_loc = os.path.join(experiment_path, f'post_training_baseline.json')
        baseline_training_config_details = file.copy()
        baseline_training_config_details["variables"].pop("sit")
        baseline_training_config_details["variables"].pop("u_drift")
        baseline_training_config_details["variables"].pop("v_drift")
        with open(file_loc, 'w') as outfile:
            json.dump(baseline_training_config_details, outfile)

    if (type == "testing"):
        print('\nGenerating baseline testing details based on your previous file...')
        file_loc = os.path.join(experiment_path, f'baseline_testing.json')
        baseline_testing_config_details = file.copy()
        baseline_testing_config_details["variables"].pop("sit")
        baseline_testing_config_details["variables"].pop("u_drift")
        baseline_testing_config_details["variables"].pop("v_drift")
        with open(file_loc, 'w') as outfile:
            json.dump(baseline_testing_config_details, outfile)
    return
    
XP = input(str(f'EXPERIMENT ID: '))
experiment_path = os.path.join(os.getcwd(), XP)
if not os.path.isfile(experiment_path):
    os.makedirs(experiment_path)

print(f'Generating configuration file...')
pre_train = input(str("Perform pre-training? (y/n):")).lower()

if (pre_train == "y"):
    print('Input details for transfer learning pre training...')
    input_details(pre_train_config_details, "pre_training")

print('\nInput details for post-stage training....')
input_details(post_train_config_details, "post_training")

print('\nInput details for testing....')
input_details(testing_config_details, "testing")

