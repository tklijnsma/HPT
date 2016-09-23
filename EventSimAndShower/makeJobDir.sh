#!/bin/bash

# Set some fixed paths and load global functions
trap - RETURN
. setJobEnv.sh

# Remember from which directory the script was called
STARTDIR="$(pwd)"

# Clean up function that runs upon receiving return signal
function makeJobDir_cleanUp {
    SCRIPTNAME=$( basename "${BASH_SOURCE[0]}" )
    echo
    echo "==== End of ${SCRIPTNAME} ====="
    cd $STARTDIR
    return
}
trap makeJobDir_cleanUp RETURN

# Enter the directory where the script is
RUNDIR=$(dirname $( fullpath "${BASH_SOURCE[0]}" ))
cd $RUNDIR


########################################
# Check if existing tarball was passed
########################################

# Check whether an argument was given to the script, and if it is a file
if [ $# -ne 1 ] ; then
    tarball_error
    return 1
elif [ ! -f $1 ]; then
    tarball_error
    return 1
else
    TARBALL="$(fullpath $1)"
    echo "Found proper tarball: $TARBALL"
fi


########################################
# Set up directory structure
########################################

# ======================================
# Base directory

# Base directory for execution of this tarball
export BASEDIR=$(basedir $TARBALL)
echo "Setting up directory called $BASEDIR and entering"
mkdir -p $BASEDIR
cd $BASEDIR


# ======================================
# CMSSW

echo "Setting up CMSSW"
echo "    SCRAM_ARCH = $SCRAM_ARCH"
echo "    CMSSW_VERSION = $CMSSW_VERSION"

if [ -r $CMSSW_VERSION/src ] ; then 
    echo "    Found existing $CMSSW_VERSION; not recreating"
else
    echo "    Executing scram p CMSSW $CMSSW_VERSION"
    scram p CMSSW $CMSSW_VERSION
fi

cd $CMSSW_VERSION/src
eval `scram runtime -sh`


# ======================================
# Creating the fragments and configurations

echo "Copying in fragments"

FRAGMENTDIR="$(pwd)/$RELATIVE_FRAGMENTDIR"
mkdir -p $FRAGMENTDIR

# Use a script to create the EventSim fragment in the fragment directory
python $RUNDIR/Scripts/Make_run_gridpack_fragment.py $TARBALL 20000 > $FRAGMENTDIR/$EVENTSIM_FRAGMENT

# Fragment for showering is just a standard file
cp $RUNDIR/Scripts/Shower_fragment.py $FRAGMENTDIR/$SHOWER_FRAGMENT

echo "Compiling fragments"
scram b

return