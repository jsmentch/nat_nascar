from scipy.io import loadmat

#need to run with singularity container /om2/user/jsmentch/projects/nat_img/.datalad/environments/analysis/image
import nascar_utility
import hcp_utils as hcp
import sys
from scipy.io import loadmat
import numpy as np
# Add the directory containing the function to the system path
from matplotlib import pyplot as plt
from nilearn import plotting
import nibabel as nb

# Import the function from the file
import matplotlib.gridspec as gridspec
from PIL import Image


def load_nascar(task):
    outputs_file=f'../data/nascar_output/all_ses-HBNsiteRU_task-{task}_results.mat'
    gbs_file=f'../data/nascar_output/all_ses-HBNsiteRU_task-{task}_GBS.mat'

    mat_contents = loadmat(outputs_file)
    U2=mat_contents['U2']
    lambda2=mat_contents['lambda2']
    mat_contents = loadmat(gbs_file)
    Y=mat_contents['Y']
    O=mat_contents['O']
    components=U2[0][0]
    temporal_modes=U2[1][0]
    contributions=U2[2][0]
    # print(task)
    # print('O',O.shape, '       #orthogonal transformation matrix TxTxS')
    # print('Y',Y.shape, '       #group atlas TxV')
    # print('components', components.shape)
    # print('temporal_modes',temporal_modes.shape)
    # print('contributions',contributions.shape)
    # print('lambda2',lambda2.shape)
    return O,Y,components,temporal_modes,contributions,lambda2

def load_components_list(task):
    component_list_file=f'../data/nascar_output/all_ses-HBNsiteRU_task-{task}_good_components.txt'
    with open(f'{component_list_file}', 'r') as f:
        # read the contents of the file into a list
        component_list = [int(line.strip()) for line in f.readlines()]
    # print(f'component_list, n={len(component_list)}, ',component_list)

    return component_list


def volume_from_cifti(data, axis):
    assert isinstance(axis, nb.cifti2.BrainModelAxis)
    data = data.T[axis.volume_mask]                          # Assume brainmodels axis is last, move it to front
    volmask = axis.volume_mask                               # Which indices on this axis are for voxels?
    vox_indices = tuple(axis.voxel[axis.volume_mask].T)      # ([x0, x1, ...], [y0, ...], [z0, ...])
    vol_data = np.zeros(axis.volume_shape + data.shape[1:],  # Volume + any extra dimensions
                        dtype=data.dtype)
    vol_data[vox_indices] = data                             # "Fancy indexing"
    return nb.Nifti1Image(vol_data, axis.affine)             # Add affine for spatial interpretation




def plot_subcor_par(to_plot,task,par_n,c):
#cifti = nb.load('../../nat_img/sourcedata/data/budapest/brain/sub-sid000007_task-movie_run-1_space-fsLR_den-91k_bold.dtseries.nii')
    cifti = nb.load('../data/HBN/clean/sub-NDARAA306NT2/ses-HBNsiteRU/sub-NDARAA306NT2_ses-HBNsiteRU_task-movieDM_space-fsLR_den-91k_bold_clean_smooth2.dtseries.nii')
    #cifti_data = cifti.get_fdata(dtype=np.float32)
    cifti_data=to_plot
    cifti_hdr = cifti.header
    axes = [cifti_hdr.get_axis(i) for i in range(cifti.ndim)]
    bg = nb.load('../data/HCP_S1200_Atlas_Z4_pkXDZ/S1200_AverageT1w_restore.nii.gz')
    plotting.plot_stat_map(
    #    volume_from_cifti(cifti_data[0,:], axes[1]),
        volume_from_cifti(cifti_data, axes[1]),
        bg_img=bg,
        display_mode='y',
        cut_coords=(15, -5, -15),
        annotate=False,
        draw_cross=False,
        black_bg=True,
        dim=-0.5,
        colorbar=False,
        output_file='../tmp/subcortical_a.png',
#         cmap=plt.cm.bwr,
        cmap='PRGn',
        symmetric_cbar=True
    )
    plotting.plot_stat_map(
    #    volume_from_cifti(cifti_data[0,:], axes[1]),
        volume_from_cifti(cifti_data, axes[1]),
        bg_img=bg,
        display_mode='y',
        cut_coords=(-30, -45, -70),
        annotate=False,
        draw_cross=False,
        black_bg=True,
        dim=-0.5,
        colorbar=False,
        output_file='../tmp/subcortical_b.png',
#         cmap=plt.cm.bwr,
        cmap='PRGn',
        symmetric_cbar=True
    )


    fig = plt.figure(figsize=(10, 10))
    plt.title('wall of brains tensor decomposition')
    gs = gridspec.GridSpec(1, 6, wspace=0, hspace=0, top=1, bottom=0, left=0, right=1) 
    #im1 = im.crop((left, top, right, bottom))
    for i in np.arange(3):
        img = Image.open(f'../tmp/subcortical_a.png')
        width, height = img.size
        #print(width,height)
        area = (660/3*i+40, 0, 660/3*(i+1)-40, 220) #crop out the bar on right
        img = img.crop(area)
        ax= plt.subplot(gs[0,i])
        ax.imshow(img)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.axis('off')
    for i in np.arange(3):
        img = Image.open(f'../tmp/subcortical_b.png')
        width, height = img.size
        #print(width,height)
        area = (660/3*i+40, 0, 660/3*(i+1)-40, 220) #crop out the bar on right
        img = img.crop(area)
        ax= plt.subplot(gs[0,i+3])
        ax.imshow(img)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.axis('off')
    plt.savefig(f'../outputs/figures/HBN_par_subcor/{task}_{par_n}_hbn_rank{c}_tensor_decomp_par_subcor.png')
    plt.close(fig)
    
    
def plot_subcor_par_max(to_plot,task,par_n,c):
#cifti = nb.load('../../nat_img/sourcedata/data/budapest/brain/sub-sid000007_task-movie_run-1_space-fsLR_den-91k_bold.dtseries.nii')
    cifti = nb.load('../data/HBN/clean/sub-NDARAA306NT2/ses-HBNsiteRU/sub-NDARAA306NT2_ses-HBNsiteRU_task-movieDM_space-fsLR_den-91k_bold_clean_smooth2.dtseries.nii')
    #cifti_data = cifti.get_fdata(dtype=np.float32)
    cifti_data=to_plot
    cifti_hdr = cifti.header
    axes = [cifti_hdr.get_axis(i) for i in range(cifti.ndim)]
    bg = nb.load('../data/HCP_S1200_Atlas_Z4_pkXDZ/S1200_AverageT1w_restore.nii.gz')
    plotting.plot_stat_map(
    #    volume_from_cifti(cifti_data[0,:], axes[1]),
        volume_from_cifti(cifti_data, axes[1]),
        bg_img=bg,
        display_mode='y',
        cut_coords=(20, 0, -20),
        annotate=False,
        draw_cross=False,
        black_bg=True,
        dim=-0.5,
        colorbar=False,
        output_file='../tmp/subcortical_a.png',
#         cmap=plt.cm.bwr,
        cmap='PRGn',
        symmetric_cbar=True
    )
    plotting.plot_stat_map(
    #    volume_from_cifti(cifti_data[0,:], axes[1]),
        volume_from_cifti(cifti_data, axes[1]),
        bg_img=bg,
        display_mode='y',
        cut_coords=(-30, -40, -60),
        annotate=False,
        draw_cross=False,
        black_bg=True,
        dim=-0.5,
        colorbar=False,
        output_file='../tmp/subcortical_b.png',
#         cmap=plt.cm.bwr,
        cmap='PRGn',
        symmetric_cbar=True
    )


    fig = plt.figure(figsize=(10, 10))
    plt.title('wall of brains tensor decomposition')
    gs = gridspec.GridSpec(1, 6, wspace=0, hspace=0, top=1, bottom=0, left=0, right=1) 
    #im1 = im.crop((left, top, right, bottom))
    for i in np.arange(3):
        img = Image.open(f'../tmp/subcortical_a.png')
        width, height = img.size
        #print(width,height)
        area = (660/3*i+40, 0, 660/3*(i+1)-40, 220) #crop out the bar on right
        img = img.crop(area)
        ax= plt.subplot(gs[0,i])
        ax.imshow(img)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.axis('off')
    for i in np.arange(3):
        img = Image.open(f'../tmp/subcortical_b.png')
        width, height = img.size
        #print(width,height)
        area = (660/3*i+40, 0, 660/3*(i+1)-40, 220) #crop out the bar on right
        img = img.crop(area)
        ax= plt.subplot(gs[0,i+3])
        ax.imshow(img)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.axis('off')
    plt.savefig(f'../outputs/figures/HBN_par_subcor_max/{task}_{par_n}_hbn_rank{c}_tensor_decomp_par_subcor.png')
    plt.close(fig)
    
    
    
    
def plot_subcor(to_plot,task,c,inv):
#inv is just for naming; inv='_inv' appends '_inv' to ouputfilename
    #cifti = nb.load('../../nat_img/sourcedata/data/budapest/brain/sub-sid000007_task-movie_run-1_space-fsLR_den-91k_bold.dtseries.nii')
    cifti = nb.load('../data/HBN/clean/sub-NDARAA306NT2/ses-HBNsiteRU/sub-NDARAA306NT2_ses-HBNsiteRU_task-movieDM_space-fsLR_den-91k_bold_clean_smooth2.dtseries.nii')
    #cifti_data = cifti.get_fdata(dtype=np.float32)
    cifti_data=to_plot
    cifti_hdr = cifti.header
    axes = [cifti_hdr.get_axis(i) for i in range(cifti.ndim)]
    bg = nb.load('../data/HCP_S1200_Atlas_Z4_pkXDZ/S1200_AverageT1w_restore.nii.gz')
    plotting.plot_stat_map(
    #    volume_from_cifti(cifti_data[0,:], axes[1]),
        nascar_utility.volume_from_cifti(cifti_data, axes[1]),
        bg_img=bg,
        display_mode='y',
        cut_coords=(20, 0, -20),
        annotate=False,
        draw_cross=False,
        black_bg=True,
        dim=-0.5,
        colorbar=False,
        output_file='../tmp/subcortical_a.png',
#         cmap=plt.cm.bwr,
        cmap='PRGn',
        symmetric_cbar=True
    )
    plotting.plot_stat_map(
    #    volume_from_cifti(cifti_data[0,:], axes[1]),
        nascar_utility.volume_from_cifti(cifti_data, axes[1]),
        bg_img=bg,
        display_mode='y',
        cut_coords=(-30, -40, -60),
        annotate=False,
        draw_cross=False,
        black_bg=True,
        dim=-0.5,
        colorbar=False,
        output_file='../tmp/subcortical_b.png',
#         cmap=plt.cm.bwr,
        cmap='PRGn',
        symmetric_cbar=True
    )


    fig = plt.figure(figsize=(10, 10))
    plt.title('wall of brains tensor decomposition')
    gs = gridspec.GridSpec(1, 6, wspace=0, hspace=0, top=1, bottom=0, left=0, right=1) 
    #im1 = im.crop((left, top, right, bottom))
    for i in np.arange(3):
        img = Image.open(f'../tmp/subcortical_a.png')
        width, height = img.size
        #print(width,height)
        area = (660/3*i+40, 0, 660/3*(i+1)-40, 220) #crop out the bar on right
        img = img.crop(area)
        ax= plt.subplot(gs[0,i])
        ax.imshow(img)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.axis('off')
    for i in np.arange(3):
        img = Image.open(f'../tmp/subcortical_b.png')
        width, height = img.size
        #print(width,height)
        area = (660/3*i+40, 0, 660/3*(i+1)-40, 220) #crop out the bar on right
        img = img.crop(area)
        ax= plt.subplot(gs[0,i+3])
        ax.imshow(img)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.axis('off')
    plt.savefig(f'../outputs/figures/HBN_23_subcor/{task}_hbn_rank{c}_tensor_decomp_subcor{inv}.png')
    plt.close(fig)
    
    
    
