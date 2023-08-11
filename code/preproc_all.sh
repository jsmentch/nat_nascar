#!/bin/bash
#SBATCH -t 0:30:00
#SBATCH -c 1
# #SBATCH -x node[054-060,100-115]
#SBATCH --mem=10G
#SBATCH -p use-everything

hostname

source /om2/user/jsmentch/anaconda/bin/activate nilearn

source /etc/profile.d/modules.sh
module use /cm/shared/modulefiles
module load openmind/hcp-workbench/1.2.3

args=($@)
subjs=(${args[@]:1})

# index slurm array to grab subject
#SLURM_ARRAY_TASK_ID=0
sub=${subjs[${SLURM_ARRAY_TASK_ID}]}
IN_DIR="/nese/mit/group/sig/projects/hbn/hbn_bids/derivatives/fmriprep_23.0.0/$sub/ses-*/func"
WRK_DIR="/om2/scratch/tmp/$(whoami)/HBN_scratch/" # assign working directory
OUT_DIR=$1

# IN_DIR=$1
# WRK_DIR=$2
# OUT_DIR=$3

SPACE="space-fsLR_den-91k_bold"
mkdir -p $WRK_DIR
mkdir -p $OUT_DIR

#FIND ALL DTSERIES IN THE FOLDER
#for F in $(find "$IN_DIR/" -name "*bold.dtseries.nii"); do
for F in $IN_DIR/*bold.dtseries.nii; do
    if [[ ! $F == *peer* ]]
    then


        printf "\n~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~\n"
        printf " ~ ~ ~ ~ ~ ~  processing $F \n"
        printf "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~\n\n"

        #SETUP VARIABLES
        F_BASE=$(basename "$F")
        #F_BASE=${F_BASE/./_}
        D1=$(dirname "$F")
        func=$(basename "$D1")
        D2=$(dirname "$D1")
        SES=$(basename "$D2")
        D3=$(dirname "$D2")
        SUB=$(basename "$D3")
        F_BASE_BASE=${F_BASE%.*.*} # filename with no extensions
        TASK="${F_BASE_BASE#*$SUB\_$SES\_}"
        TASK="${TASK%%_$SPACE}"
        WRK_DIR_SES=$WRK_DIR$SUB/$SES
        mkdir -p $WRK_DIR_SES
        # cd $IN_DIR
        # echo "datalad get the file"
        # datalad get ${F}
        # cd ~-
        mkdir -p $OUT_DIR/$SUB/$SES

        cp -nrL $F $WRK_DIR_SES/${SUB}_${SES}_${TASK}_$SPACE.dtseries.nii


        #REMOVE CONFOUNDS with nilearn
        echo "----------------------CONFOUNDS----------------------"
        date

        CONFOUNDS=$WRK_DIR_SES/${SUB}_${SES}_${TASK}_desc-confounds_timeseries.tsv
        cp -nrL $D1/${SUB}_${SES}_${TASK}_desc-confounds_timeseries.tsv $CONFOUNDS
        # cd $IN_DIR
        # echo "datalad get the confounds"
        # datalad get $D1/$SUB\_$SES\_$TASK\_desc-confounds_timeseries.*
        # cd -
        CLEAN=$OUT_DIR/$SUB/$SES/${SUB}_${SES}_${TASK}_${SPACE}_clean.dtseries.nii
        if [ ! -f $CLEAN ]
        then
            CLEAN_CMD="python preproc_all_confounds.py $WRK_DIR_SES/${SUB}_${SES}_${TASK}_${SPACE}.dtseries.nii $CLEAN $CONFOUNDS"
            echo $'Command :\n'${CLEAN_CMD}
            ${CLEAN_CMD}
            # cd $IN_DIR
            # echo "datalad drop the confounds"
            # datalad drop $D1/$SUB\_$SES\_$TASK\_desc-confounds_timeseries.*
            # cd -
        else
            echo "already cleaned, skip"
        fi
        rm $CONFOUNDS
        date

        #SMOOTH with workbench
        echo "----------------------SMOOTHING----------------------"
        date
        SMOOTHED2=$OUT_DIR/$SUB/$SES/${SUB}_${SES}_${TASK}_${SPACE}_clean_smooth2.dtseries.nii
        if [ ! -f $SMOOTHED2 ]
        then
            WORKBENCH_CMD="wb_command -cifti-smoothing \
            $CLEAN \
            2 2 COLUMN \
            ${SMOOTHED2} \
            -left-surface /om2/user/jsmentch/data/datalad/templateflow/tpl-fsLR/tpl-fsLR_hemi-L_den-32k_sphere.surf.gii \
            -right-surface /om2/user/jsmentch/data/datalad/templateflow/tpl-fsLR/tpl-fsLR_hemi-R_den-32k_sphere.surf.gii"
            echo $'Command :\n'${WORKBENCH_CMD}
            ${WORKBENCH_CMD}
        else
            echo "already ran, skip"
        fi
        # cd $IN_DIR
        # echo "datalad drop the file"
        # datalad drop ${F}
        # cd ~-
        date

        SMOOTHED4=$OUT_DIR/$SUB/$SES/${SUB}_${SES}_${TASK}_${SPACE}_clean_smooth4.dtseries.nii
        if [ ! -f $SMOOTHED4 ]
        then
            WORKBENCH_CMD="wb_command -cifti-smoothing \
            $CLEAN \
            4 4 COLUMN \
            ${SMOOTHED4} \
            -left-surface /om2/user/jsmentch/data/datalad/templateflow/tpl-fsLR/tpl-fsLR_hemi-L_den-32k_sphere.surf.gii \
            -right-surface /om2/user/jsmentch/data/datalad/templateflow/tpl-fsLR/tpl-fsLR_hemi-R_den-32k_sphere.surf.gii"
            echo $'Command :\n'${WORKBENCH_CMD}
            ${WORKBENCH_CMD}
        else
            echo "already ran, skip"
        fi
        # cd $IN_DIR
        # echo "datalad drop the file"
        # datalad drop ${F}
        # cd ~-
        date

        #PARCELLATE mmp
        echo "----------------------PARCELLATE----------------------"
        date
        PARCELLATED=$OUT_DIR/$SUB/$SES/${SUB}_${SES}_${TASK}_${SPACE}_clean_smooth2_mmp.ptseries.nii

        if [ ! -f $PARCELLATED ]
        then
            PARCEL_CMD="wb_command -cifti-parcellate \
            ${SMOOTHED2} \
            /nese/mit/group/sig/projects/naturalistic/nat_img/sourcedata/data/parcellations/Q1-Q6_RelatedValidation210.CorticalAreas_dil_Final_Final_Areas_Group_Colors.32k_fs_LR.dlabel.nii \
            COLUMN \
            $PARCELLATED"
            echo $'Command :\n'${PARCEL_CMD}
            ${PARCEL_CMD}
            date
        else
            echo "already parcellated, skip"
        fi
    else
        echo "skipping peer eye run"
    fi
done

rm -r $WRK_DIR$SUB

echo "completed!"


#n./preproc_all.sh /om2/user/jsmentch/projects/nat_img/sourcedata/data/cneuromod/friends.fmriprep/sub-01/ses-001/func/ /om2/scratch/Wed/jsmentch/scratch /om2/scratch/Wed/jsmentch/output

#./preproc_all.sh /om2/scratch/Thu/jsmentch/fmriprep_hbn100/derivatives/sub-NDARAC904DMU/ses-HBNsiteRU/func/ /om2/scratch/Wed/jsmentch/scratch /om2/scratch/Wed/jsmentch/hbn_output
