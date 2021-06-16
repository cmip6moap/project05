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

hist_model_data_dir = "/badc/cmip6/data/CMIP6/CMIP/*/*/historical/*/Amon/ua/gn/latest/"
hist_data_in_dir_paths = glob(hist_model_data_dir)
hist_models = {}
for i in range(0,len(hist_data_in_dir_paths)):
    model_name = hist_data_in_dir_paths[i].split(sep='/')[7]
    if model_name not in hist_models:
        hist_models[model_name] = [hist_data_in_dir_paths[i].split(sep='/')[9]] # assign member to list
    else:
        hist_models[model_name].append(hist_data_in_dir_paths[i].split(sep='/')[9])


model_id = int(os.environ["model_id"])
model = list(hist_models.keys())[model_id]
for member in hist_models[model]:
    hist_model_data_dir = "/badc/cmip6/data/CMIP6/CMIP/*/"+ str(model)+'/historical/'+str(member)+'/Amon/ua/gn/latest/*'
    hist_model_data_in_dir_paths = glob(hist_model_data_dir)
    ds_n = xr.open_mfdataset(hist_model_data_in_dir_paths)
    try : 
        ds_n = ds_n.rename({'latitude':'lat', 'longitude':'lon'})
    except ValueError :
        pass
    ds_n = ds_n.mean(dim='lon').sel(lat=slice(0, 90))
    is_winter = ds_n['time'].dt.season == 'DJF'
    ds_n_winter = ds_n.isel(time=is_winter)
    ds_n_winter_mean = ds_n_winter.sel(time=slice(str(start_year)+'-01-16', str(end_year)+'-12-16')).mean(dim='time')

    outdir='/home/users/cjm317/CMIP6_Hackathon/Historical'
    outfile=f'{model}_{member}_DJF_zonal_mean_ua_Amon_'+str(start_year)+'-'+str(end_year)+'.nc'
    if not os.path.exists(outdir):
        cmd = 'mkdir -p {}'.format(outdir)
        shellcmd(cmd, 'created filepath')
    ds_n_winter_mean.to_netcdf(f'{outdir}/{outfile}')

