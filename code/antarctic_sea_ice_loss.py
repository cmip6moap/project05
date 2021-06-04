import xarray as xar
import matplotlib.pyplot as plt
import numpy as np
import os
# from available_models import available_models_dict, available_models_futAntSIC_dict
from search_for_data import find_unique_ens_members
import pdb

#define some variables related to the experiment we're interested in

base_dir = '/gws/pw/j05/cop26_hackathons/bristol/project05/data_from_ESM/'
base_dir_badc = '/badc/cmip6/data/CMIP6/PAMIP/'

var_name = 'ua' #begin with zonal wind, ua
table_id='Amon'

mip_id = 'PAMIP'

version_name='latest'
experiment = 'pdSST-futAntSIC'

force_recalculate=False

#use a glob-based function to find all the data we can use for a given experiment. 
print('finding all available data')
available_models_dict_to_use = find_unique_ens_members(base_dir, base_dir_badc, var_name, experiment)
print('done finding all available data')

#loop over each model 

for model_name in available_models_dict_to_use.keys():
    print(f'working on {model_name}')
    #get the dict of parameters for just this model
    model_specific_dict = available_models_dict_to_use[model_name]

    #define some model specific parameters
    ens_idx_start=1
    ens_idx_end=model_specific_dict['n_ens']
    ens_id_list = model_specific_dict['ens_ids']
    files_list = model_specific_dict['files']

    #setup a place to output the data

    out_dir = f'/home/users/sit204/data/{mip_id}/{experiment}/{model_name}/'
    out_name = f'{var_name}_zonal_mean_ens_mean_{ens_idx_start}_{ens_idx_end}.nc'

    #create the output directory if it doesn't already exist

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    #if the data has not already been processed, or if we're forcing a recalculate then proceed:
    if not os.path.isfile(f'{out_dir}/{out_name}') or force_recalculate:

        data_out_dict = {}

        #loop over ensemble members
        for ens_idx in ens_id_list:

            #find the file or files associated with each ensemble member for a particular variable 

            file_names_list = [filename for filename in files_list if ens_idx in filename ]

            variant_label = ens_idx

            print(f'opening ensemble member {variant_label} for {model_name}')

            #construct corresponding directory on Jasmin

            #most models only have 1 file per ensemble member, but some have multiple. Read them in differently.
            if int(model_specific_dict['n_files_per_ens_member'])==1:

                #create xarray dataset using constructed filename
                dataset = xar.open_dataset(file_names_list[0])
                
            elif model_specific_dict['n_files_per_ens_mem']==2:

                #create xarray dataset using constructed filename
                dataset = xar.open_mfdataset(file_names_list)
            else:
                raise NotImplementedError('Can only deal with 1 or 2 files at the moment')

            #resample for 2 years just to be quick
            # dataset_sub = dataset.sel(time=slice(str(start_year_file), str(start_year_file+2)))
            dataset_sub = dataset

            #calculate monthly means
            var_mean = dataset_sub[var_name].groupby('time.month').mean('time')

            #select DJFM
            var_winter_mean = var_mean.where(np.logical_or(var_mean.month<=3, var_mean.month==12), drop=True)
            zonal_var_winter_mean = var_winter_mean.mean(('month', 'lon'))

            data_out_dict[variant_label] = zonal_var_winter_mean

        #put all entries in the data_out_dict into array to mean over

        dict_keys_list = [key for key in data_out_dict.keys()]

        n_ens_members = len(dict_keys_list)
        nplev = dataset['plev'].shape[0]
        nlat = dataset['lat'].shape[0]

        ens_members_array = np.zeros((n_ens_members, nplev, nlat))

        for key_idx in range(n_ens_members):
            ens_members_array[key_idx,...] = data_out_dict[dict_keys_list[key_idx]].values

        #perform ensemble mean

        ens_mean_array = np.mean(ens_members_array, axis=0)

        #create new blank dataset
        ens_mean_dataset=xar.Dataset(coords=dataset.coords)

        ens_mean_dataset.coords['ens_idx'] = ('ens_idx', np.arange(n_ens_members))

        #put zonal mean of each ensemble member into an array
        ens_mean_dataset['ua_DJFM_zm'] = (('ens_idx', 'plev', 'lat'), ens_members_array)

        #put the ensemble and zonal mean into an array
        ens_mean_dataset['ua_DJFM_zm_ens_mean'] = (('plev', 'lat'), ens_mean_array)

        #save the output to a netcdf file
        ens_mean_dataset.to_netcdf(f'{out_dir}/{out_name}')
