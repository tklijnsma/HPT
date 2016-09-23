#!/bin/bash

# Set some fixed paths and load global functions
trap - RETURN
. setJobEnv.sh

# Remember from which directory the script was called
STARTDIR="$(pwd)"

# Enter the directory where the script is
SCRIPTDIR=$(dirname $( fullpath "${BASH_SOURCE[0]}" ))
cd $SCRIPTDIR

# Clean up function that runs upon receiving return signal
function clean_up {
    SCRIPTNAME=$( basename "${BASH_SOURCE[0]}" )
    echo
    echo "==== End of ${SCRIPTNAME} ====="
    cd $STARTDIR
    # trap - RETURN
    return
}
trap clean_up RETURN


########################################
# Deal with input arguments
########################################

# Required arguments:
# - Tarball
# - Number of events needed
# - Some job numbering scheme

function argument_failure {
    echo "Error detected in input parameters"
    echo "Usage:"
    echo ". runJob.sh path_to_tarball number_of_events number_of_job"
    return 1
}

# Check whether enough arguments were passed
if [ $# -ne 3 ] ; then
    argument_failure
    return 1
fi

TARBALL=$1
NEVENTS=$2
JOBNUM=$3

if [ ! -f $TARBALL ]; then
    tarball_error
    return 1
fi

# --> Better to just set up directory structure and compilation once
# # Set-up the directory structure and (re)create the fragments
# # (nothing happens if it already exists)
# (
#     source makeJobDir.sh $TARBALL
# )
# # If makeJobDir failed, return
# if [ $? -ne 0 ]; then
#     return 1
# fi
# echo


########################################
# Set environment
########################################

export BASEDIR="$(basedir $TARBALL)"
cd $BASEDIR/$CMSSW_VERSION/src

echo "Setting environment for $CMSSW_VERSION"
eval `scram runtime -sh`


########################################
# Create cfg files
########################################

EVENTSIM_OUTPUT_ROOTFILE="Unshowered${JOBNUM}.root"
SHOWER_OUTPUT_ROOTFILE="Showered${JOBNUM}.root"


# Relative to ${CMSSW_VERSION}/src
CFG_DIR="cfg${JOBNUM}"
mkdir -p "${CFG_DIR}"
cd $CFG_DIR


EVENTSIM_CFG="EventSim_cfg_${JOBNUM}.py"
cmsDriver.py "${RELATIVE_FRAGMENTDIR}${EVENTSIM_FRAGMENT}" \
    --fileout file:"${EVENTSIM_OUTPUT_ROOTFILE}" \
    --mc \
    --eventcontent LHE \
    --datatier LHE \
    --conditions MCRUN2_71_V1 \
    --step LHE \
    --python_filename "${EVENTSIM_CFG}" \
    --customise Configuration/DataProcessing/Utils.addMonitoring \
    -n $NEVENTS \
    --no_exec
    # --runsAndWeightsForMC [[$JOBNUM,1]]

# Hack in the piece of code that sets the rng seed randomly
echo "Adding the randomly set rng seed into ${EVENTSIM_CFG}"
python $setJobEnv_dir/cfgHacker.py $EVENTSIM_CFG


SHOWER_CFG="Shower_cfg_${JOBNUM}.py"
cmsDriver.py "${RELATIVE_FRAGMENTDIR}${SHOWER_FRAGMENT}" \
    --filein file:"${EVENTSIM_OUTPUT_ROOTFILE}" \
    --fileout file:"Showered${JOBNUM}.root" \
    --mc \
    --eventcontent RAWSIM \
    --customise SLHCUpgradeSimulations/Configuration/postLS1Customs.customisePostLS1,Configuration/DataProcessing/Utils.addMonitoring \
    --datatier GEN \
    --inputCommands 'keep *','drop LHEXMLStringProduct_*_*_*' \
    --conditions MCRUN2_71_V1 \
    --step GEN \
    --magField 38T_PostLS1 \
    --python_filename "${SHOWER_CFG}" \
    -n $NEVENTS \
    --no_exec


echo "Doing cmsRun ${EVENTSIM_CFG}"
cmsRun $EVENTSIM_CFG
echo

sleep 5

echo "Doing cmsRun ${SHOWER_CFG}"
cmsRun $SHOWER_CFG
echo
