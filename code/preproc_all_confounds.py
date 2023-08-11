import numpy as np
import pandas as pd

# import matplotlib as mpl
# import matplotlib.pyplot as plt
# import seaborn as sns
# sns.set("paper", "white")

from nilearn.image import load_img
from nilearn.signal import clean
from os import mkdir

# from utility import var_to_nan
from pathlib import Path
import nibabel as nib
import sys

input_file=str(sys.argv[1])
output_file=str(sys.argv[2])
input_confounds = str(sys.argv[3])

if not Path(output_file).is_file(): # if output doesn't exist already, run it
    if Path(input_file).is_file(): # if input doesn't exist, skip
        print(f'running {input_file}')
        #clean
        data = pd.read_csv(input_confounds, sep='\t')
        #load confounds
        try:
            confound_names=list(data)
            motion=[s for s in confound_names if 'motion' in s] #get motion outliers
            cosine=[s for s in confound_names if 'cosine' in s] #get all of the cosine regressors
            acomp=[s for s in confound_names if 'a_comp_cor' in s][:5] #get the first 5 acomp_cor regressors
            confounds_list = ['csf', 'framewise_displacement', 'rot_x','rot_y','rot_z','trans_x','trans_y','trans_z']
            confounds_list.extend(motion)
            confounds_list.extend(cosine)
            confounds_list.extend(acomp)
            confounds=data[confounds_list].to_numpy()
            confounds = np.nan_to_num(confounds)
            #load brain data
            brainimg = load_img(input_file) # load func img
            func_data=np.array(brainimg.dataobj)
            #func_data = var_to_nan(func_data,0.5)
            #clean
            func_data_clean = clean(func_data,detrend=False,confounds=confounds)
            func_cln = nib.Cifti2Image(func_data_clean, brainimg.header)
            #export
            func_cln.to_filename(output_file)
        except:
            print('confounds missing or ERROR, skip')
    else:
        print('input dne ',input_file)
else:
    print(f'skipping {output_file}, already ran')