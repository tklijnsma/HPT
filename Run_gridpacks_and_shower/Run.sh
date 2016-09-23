#!/bin/bash

STARTDIR="$(pwd)"

########################################
# Check if executed from the proper directory
########################################

SHOULDBERUNDIR="$(basename "$(pwd)")"
if [ "$SHOULDBERUNDIR" != "Run_gridpacks_and_shower" ]; then
    echo "Error: Not executed from the proper directory"
    echo "       Current directory should be Run_gridpacks_and_shower, but is $SHOULDBERUNDIR"
    return 1
fi

RUNDIR="$(pwd)"

########################################
# Check input arguments
########################################

if [ $# -eq 0 ] || [ $# -eq 1 ]; then
    echo "    No arguments supplied"
    echo "    1st argument: Supply the name of one of the following files:"
    ls ../Make_gridpacks/Saved_tarballs
    echo "    2nd argument: Supply the desired number of events"
    return 1
fi

export RUNNAME="$1"
export NEVENTS="$2"

# Need full path of the tarball
cd ../Make_gridpacks/Saved_tarballs/
TARBALL="$(pwd)/$RUNNAME.tgz"
cd $RUNDIR

if [ ! -f $TARBALL ]; then
    echo "Error: Tarball $TARBALL does not exist!"
    return 1
fi


########################################
# Create directory and copy necessary scripts
########################################

echo "Setting up directory for $RUNNAME"

# Create directory if it does not yet exist
if [ ! -d $RUNNAME ]; then
    mkdir -p $RUNNAME
else
    echo "    Directory $RUNNAME already exists"
fi

# Copy in all necessary scripts (should overwrite already existing .sh's)
echo "    Copying in scripts"
cp Scripts/Set_CMSSW.sh $RUNNAME/Set_CMSSW.sh


########################################
# Work
########################################

cd $RUNNAME

# Create CMSSW if necessary and set environment
source Set_CMSSW.sh

# ======================================
# Fragments

# Create the fragments
FRAGMENTDIR=$CMSSW_VERSION/src/Configuration/GenProduction/python/
mkdir -p $FRAGMENTDIR

# Fragment for running the gridpack requires some input
python ../Scripts/Make_run_gridpack_fragment.py $TARBALL 20000 > $FRAGMENTDIR/Run_gridpack_fragment.py

# Fragment for showering is just 1 file
cp ../Scripts/Shower_fragment.py $FRAGMENTDIR/Shower_fragment.py

# ======================================
# Run driver scripts

echo "Compiling fragments"
cd $CMSSW_VERSION/src
scram b
cd ../..

export X509_USER_PROXY=$HOME/private/personal/voms_proxy.cert

echo "Attempting to run the Run_gridpack driver"
export RUN_FRAGMENT=Configuration/GenProduction/python/Run_gridpack_fragment.py
cmsDriver.py $RUN_FRAGMENT --fileout file:Unshowered.root --mc --eventcontent LHE --datatier LHE --conditions MCRUN2_71_V1 --step LHE --python_filename Run_gridpack_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n $NEVENTS || exit $? ;
echo

echo "Attempting to run the Shower driver"
export FRAGMENT_PY=Configuration/GenProduction/python/Shower_fragment.py
cmsDriver.py $FRAGMENT_PY --filein file:Unshowered.root --fileout file:Showered.root --mc --eventcontent RAWSIM --customise SLHCUpgradeSimulations/Configuration/postLS1Customs.customisePostLS1,Configuration/DataProcessing/Utils.addMonitoring --datatier GEN --inputCommands 'keep *','drop LHEXMLStringProduct_*_*_*' --conditions MCRUN2_71_V1 --step GEN --magField 38T_PostLS1 --python_filename Shower_cfg.py --no_exec -n $NEVENTS
echo


echo "Doing cmsRun Run_gridpack_cfg.py"
cmsRun Run_gridpack_cfg.py
echo

sleep 5

echo "Doing cmsRun Shower_cfg.py"
cmsRun Shower_cfg.py
echo


cd $STARTDIR