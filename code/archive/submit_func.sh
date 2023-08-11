#!/bin/bash
subjs=($@)

base=/nese/mit/group/sig/projects/hbn/hbn_bids/

if [[ $# -eq 0 ]]; then
    # first go to data directory, grab all subjects,
    # and assign to an array
    #pushd /nese/mit/group/sig/projects/hbn/hbn_bids/derivatives/freesurfer_7.3.2/
    #pushd /nese/mit/group/sig/projects/hbn/hbn_bids/derivatives/xcp_d_0.4.0rc1_old/
    #pushd /nese/mit/group/sig/projects/hbn/hbn_bids/derivatives/qsirecon/
    pushd $base
    subjs=($(ls sub-* -d))
    #pushd $base
    #subjs=($(ls sub-*/*CBIC*/dwi -d))
    #subjs=("${subjs[@]///ses-HBNsiteCBIC}")
    #subjs=("${subjs[@]///dwi}")
    popd
fi

# take the length of the array
# this will be useful for indexing later
len=$(expr ${#subjs[@]} - 1) # len - 1

echo Spawning ${#subjs[@]} sub-jobs.

sbatch --array=0-$len%100 $base/code/sfc/ss_func.sh $base ${subjs[@]}
