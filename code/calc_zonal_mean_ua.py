''' Calculates zonal mean zonal wind for CMIP6 or PAMIP models, one file is produced for each ensemble member.'''


# ==========================================================================================
# Imports
# ==========================================================================================

import xarray as xar
import matplotlib.pyplot as plt
import numpy as np
import os
import glob

# ==========================================================================================
# Global variables
# ==========================================================================================

var_name = 'ua' #begin with zonal wind, ua
table_id='Amon'
experiment = 'piControl'
version_name='latest'
grid_type = 'gn' #gn is model native grid
plev_for_analysis = 1000. 
           
# ==========================================================================================
# Functions
# ==========================================================================================

def calculate_zonal_mean(data, var_name, plev_for_analysis):
    # Calculate monthly means
    var_mean = data[var_name].groupby('time.month').mean('time')
    # Select DJFM
    var_winter_mean = var_mean.where(np.logical_or(var_mean.month<=3, var_mean.month==12), drop=True)
    # Select pressure value
    var_winter_mean_plev = var_winter_mean.sel(plev=plev_for_analysis, method='nearest')
    return var_winter_mean_plev

def zonal_plot(data, model_name, var_name, plev_for_analysis):
    try:
        data.mean(('month', 'lon')).plot.line(label=model_name)
    except:
        data.mean(('month', 'longitude')).plot.line(label=model_name)

    plt.xlim(0., 90.)
    plt.ylabel(f'Zonal and DJFM mean {var_name} at {plev_for_analysis/100.}hPa')
    plt.xlabel('Latitude (degrees)')
    plt.title(f'CMIP6 comparison of DJFM mean zonal-mean {var_name}')
    plt.legend()

# ==========================================================================================
# Main
# ==========================================================================================

model_centres = [os.path.basename(file) for file in glob.glob('/badc/cmip6/data/CMIP6/CMIP/*')]

for model_centre_code in model_centres:   
    model_names = os.listdir(f'/badc/cmip6/data/CMIP6/CMIP/{model_centre_code}')
    # Loop over model names within a model centre
    for model_name in model_names:

        print(f'Processing model {model_name}...')

        ensemble_list = [os.path.basename(file) for file in glob.glob(f'/badc/cmip6/data/CMIP6/CMIP/{model_centre_code}/{model_name}/{experiment}/r*')]    
        # Loop over ensemble members
        for variant_label in ensemble_list:
            outfile = f'{model_centre_code}_{model_name}_{experiment}_{variant_label}_zonalmean.nc'

            # Construct corresponding directory on Jasmin
            directory = f'/badc/cmip6/data/CMIP6/CMIP/{model_centre_code}/{model_name}/{experiment}/{variant_label}/{table_id}/{var_name}/{grid_type}/{version_name}/'

            # Create a list of filenames in an ensemble member
            filenames = glob.glob(f'{directory}*')

            # Check if there are any files in an ensemble member
            if not filenames:
                print(f"No files for model: {model_name}, realization: {variant_label}")
                continue

            # If there are files, open them all together to merge time coordinates. 
            with xar.open_mfdataset(filenames) as dataset:

                try:
                    var_winter_mean_plev = calculate_zonal_mean(data=dataset, var_name=var_name, plev_for_analysis=plev_for_analysis)
                except:
                    print(f'Invalid file: {filenames}')
                    break

                # Save each ensemble member to file.
                var_winter_mean_plev.to_netcdf(outfile)

print('End of processing script.')            
