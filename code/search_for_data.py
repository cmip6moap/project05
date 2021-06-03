import glob
import pdb

def find_ensemble_list(base_dir, var_name, exp_name, data_type='Amon',):
    '''main function that takes in a directory, variable and experiment name
    and looks for all available ensemble members, outputting a dictionary of results.
    This was inspired by Phoebe and Colin's GLOB scripts on day 1.'''

    use_badc = '/badc/' in base_dir

    models = {}

    for filename in glob.glob(f'{base_dir}/*/*'):

        model_name=filename.split('/')[-1]        

        if use_badc:
            list_of_files = glob.glob(f'{filename}/{exp_name}/*/{data_type}/{var_name}/*/latest/*.nc')            
        else:
            list_of_files = glob.glob(f'{filename}/{exp_name}/{data_type}/{var_name}/*/latest/*.nc')

        ens_id_list, n_files_per_ens_member = list_of_ensemble_ids_from_filenames(list_of_files, exp_name)

        models[model_name] = {'files':list_of_files,
                            'n_ens':len(ens_id_list),
                            'model_name': model_name,
                            'data_dir': filename,
                            'ens_ids': ens_id_list,
                            'n_files_per_ens_member':n_files_per_ens_member,
                            }
        
    return models

def list_of_ensemble_ids_from_filenames(list_of_files, exp_name):
    '''function that produces a list of unique ensemble members
    from the list of filenames'''


    ens_id_list = []

    for filename in list_of_files:
        nc_file_name = filename.split('/')[-1]
        ensemble_member_name = nc_file_name.split(exp_name)[-1].split('_')[1]
        ens_id_list.append(ensemble_member_name)

    unique_ens_id_list = list(set(ens_id_list))

    if len(unique_ens_id_list)==len(ens_id_list):
        n_files_per_ens_member = 1
    else:
       n_files_per_ens_member = len(ens_id_list)/ len(unique_ens_id_list)

    return unique_ens_id_list, n_files_per_ens_member

def find_unique_ens_members(base_dir, base_dir_badc, var_name, exp_name):
    '''PAMIP-specific problem is that we have the badc data and the
    data we've downloaded to the group workspace. This function
    combines the data from each source into one main dictionary
    that can be used by processing scripts.'''


    models = find_ensemble_list(base_dir, var_name, exp_name)
    models_badc = find_ensemble_list(base_dir_badc, var_name, exp_name)

    model_names = models.keys()
    model_badc_names = models_badc.keys()

    all_model_names = list(model_names) + list(model_badc_names)

    unique_model_names = list(set(all_model_names))

    models_combined = {}
    

    for model_name_unique in unique_model_names:
        in_models, in_models_badc, in_both =False, False, False

        if model_name_unique in model_names:
            in_models = True
        if model_name_unique in model_badc_names:
            in_models_badc = True            

        if in_models and in_models_badc:
            in_both=True

        if in_both:
            n_ens_models = models[model_name_unique]['n_ens']
            n_ens_models_badc = models_badc[model_name_unique]['n_ens']      

            if n_ens_models>n_ens_models_badc:
                models_combined[model_name_unique] = models[model_name_unique]
            elif n_ens_models<n_ens_models_badc:   
                models_combined[model_name_unique] = models_badc[model_name_unique]  
            else:
                models_combined[model_name_unique] = models[model_name_unique]                
        else:
            if in_models:
                models_combined[model_name_unique] = models[model_name_unique]
            elif in_models_badc:
                models_combined[model_name_unique] = models_badc[model_name_unique]                

        
    # for model_name in models_combined.keys():
    #     print(model_name, models_combined[model_name]['n_ens'], models_combined[model_name]['data_dir'])    

    return models_combined

if __name__=="__main__":

    base_dir = '/gws/pw/j05/cop26_hackathons/bristol/project05/data_from_ESM/'
    base_dir_badc = '/badc/cmip6/data/CMIP6/PAMIP/'
    var_name='ua'
    exp_name='pdSST-pdSIC'

    models_combined = find_unique_ens_members(base_dir, base_dir_badc, var_name, exp_name)