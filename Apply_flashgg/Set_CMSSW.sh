#!/bin/bash

########################################
# Go up in directories until Make_gridpacks is reached
########################################

STARTDIR="$(pwd)"

CURRENTDIR="$(basename "$(pwd)")"
while [ "$CURRENTDIR" != "Apply_flashgg" ]; do

    cd ..

    CURRENTDIR="$(basename "$(pwd)")"

    # If looping reaches "/", the script wasn't run from a directory in the project
    if [ "$CURRENTDIR" != "/" ]; then
        echo "Error: Can't determine the top of the project directory"
        echo "       Please execute from a directory inside the project"
        cd $STARTDIR
        return 1
    fi

done

export FLASHBASE=$(pwd)


########################################
# Set up CMSSW
########################################

echo "Setting up CMSSW"

# Set which arch and version to make
#export SCRAM_ARCH=slc6_amd64_gcc491

# These for the May results (can't recompile flashgg)
# export SCRAM_ARCH=slc6_amd64_gcc493
# export CMSSW_VERSION=CMSSW_7_6_3_patch2
export SCRAM_ARCH=slc6_amd64_gcc493
export CMSSW_VERSION=CMSSW_8_0_8_patch1


echo "    SCRAM_ARCH = $SCRAM_ARCH"
echo "    CMSSW_VERSION = $CMSSW_VERSION"

# If "renew" flag is passed, delete existing CMSSWs
if [ $# -eq 0 ]; then
    echo "    No arguments supplied"
elif [ "$1" = "renew" ] && [ -r $CMSSW_VERSION/src ]; then
    echo "    Found existing $CMSSW_VERSION; Deleting it and remaking"
    rm -rf $CMSSW_VERSION
fi    

# Create CMSSW directory if necessary
source /afs/cern.ch/cms/cmsset_default.sh
if [ -r $CMSSW_VERSION/src ] ; then 
    echo "    Found existing $CMSSW_VERSION"
else
    scram p CMSSW $CMSSW_VERSION
fi

# cmsenv
cd $CMSSW_VERSION/src
eval `scram runtime -sh`

cd ../..
echo "    Setup $CMSSW_VERSION"