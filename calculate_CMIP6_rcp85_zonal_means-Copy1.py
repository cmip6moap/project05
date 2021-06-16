from itertools import chain
from glob import glob

import matplotlib
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import re
import os
import subprocess

def shellcmd(cmd,msg_func):
    try:
        retcode=subprocess.call(cmd, shell=True)
        if retcode<0:
            print('syst. cmd terminated by signal', -retcode)
        elif retcode:
            print('syst. cmd returned in ',msg_func,' ', retcode)
    except OSError as ex:
        print("Execution failed in "+msg_func,+": ",ex)

# Set some plotting defaults
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 100

start_year = 1981
end_year = 2010

data_dir = "/badc/cmip6/data/CMIP6/ScenarioMIP/*/*/ssp585/*/Amon/ua/gn/latest"
# /badc/cmip6/data/CMIP6/{name of }/
#maybe focus on models that there are PAMIP runs for first
#but its still useful to plot for everything
#r = realization, i = initialization, p = physics, f = forcing

#!ls {data_dir}
data_in_dir_paths = glob(data_dir)
#data_in_dir_paths

rcp85_data_dir = "/badc/cmip6/data/CMIP6/ScenarioMIP/*/*/ssp585/*/Amon/ua/gn/latest"
data_in_dir_paths = glob(rcp85_data_dir)
rcp85_models = {}
for i in range(0,len(data_in_dir_paths)):
    model_name = data_in_dir_paths[i].split(sep='/')[7]
    if model_name not in rcp85_models:
        rcp85_models[model_name] = [data_in_dir_paths[i].split(sep='/')[9]] # assign member to list
    else:
        rcp85_models[model_name].append(data_in_dir_paths[i].split(sep='/')[9])

model_id = int(os.environ["model_id"])
model = list(rcp85_models.keys())[model_id]

for member in rcp85_models[model]:
    if model == 'MRI-ESM2-0':
        rcp85_model_data_in_dir_paths = '/badc/cmip6/data/CMIP6/ScenarioMIP/MRI/MRI-ESM2-0/ssp585/r1i1p1f1/Amon/ua/gn/latest/ua_Amon_MRI-ESM2-0_ssp585_r1i1p1f1_gn_206501-210012.nc'
    else:
        rcp85_model_data_dir = "/badc/cmip6/data/CMIP6/ScenarioMIP/*/"+ str(model)+'/ssp585/'+str(member)+'/Amon/ua/gn/latest/*'
        rcp85_model_data_in_dir_paths = glob(rcp85_model_data_dir)
    ds_n = xr.open_mfdataset(rcp85_model_data_in_dir_paths)
    try :
        ds_n = ds_n.rename({'latitude':'lat', 'longitude':'lon'})
    except ValueError :
        pass
    ds_n = ds_n.mean(dim='lon').sel(lat=slice(0, 90))
    is_winter = ds_n['time'].dt.season == 'DJF'
    ds_n_winter = ds_n.isel(time=is_winter)
    ds_n_winter_mean = ds_n_winter.sel(time=slice(str(start_year)+'-01-16', str(end_year)+'-12-16')).mean(dim='time')

    outdir='/home/users/cjm317/CMIP6_Hackathon/RCP85'
    outfile=f'{model}_{member}_DJF_zonal_mean_ua_Amon_'+str(start_year)+'-'+str(end_year)+'.nc'
    if not os.path.exists(outdir):
        cmd = 'mkdir -p {}'.format(outdir)
        shellcmd(cmd, 'created filepath')
    ds_n_winter_mean.to_netcdf(f'{outdir}/{outfile}')

        

