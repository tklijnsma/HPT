#!/bin/bash

STARTDIR="$(pwd)"

########################################
# Check if executed from the proper directory
########################################

SHOULDBEMAKEDIR="$(basename "$(pwd)")"
if [ "$SHOULDBEMAKEDIR" != "Make_gridpacks" ]; then
    echo "Error: Not executed from the proper directory"
    echo "       Current directory shoulb be Make_gridpacks, but is $SHOULDBEMAKEDIR"
    return 1
fi

MAKEDIR="$(pwd)"

########################################
# Check input arguments
########################################

if [ $# -eq 0 ]; then
    echo "    No arguments supplied"
    echo "    Supply the name of one of the following directories:"
    echo "    $(ls input)"
    return 1
fi

RUNNAME="$1"

########################################
# Check if there is an input card
########################################

cd input/$RUNNAME

# Read which input card; if multiple, take the first one
INPUTCARD="$(ls *.input | head -n 1)"

# If no input card found
if [ -z "$INPUTCARD" ]; then
    echo "Could not find a .input file in input/$RUNNAME"
    cd $STARTDIR
    return 1
fi


########################################
# Set the MODEL (there should be a MODEL.txt file)
########################################

MODEL="$(cat MODEL.txt)"

if [ -z "$MODEL" ]; then
    echo "Could not find a MODEL.txt file in input/$RUNNAME"
    cd $STARTDIR
    return 1

elif [ "$MODEL" = "gg_H" ]; then
    PWGPY="run_pwg_V1.py"
elif [ "$MODEL" = "gg_H_quark-mass-effects" ]; then
    PWGPY="run_pwg.py"

else
    echo "Unknown model $MODEL"
    cd $STARTDIR
    return 1
fi


echo "------------------------------------------------------------------"
echo "Starting a run"
echo "    RUNNAME   = $RUNNAME"
echo "    INPUTCARD = $INPUTCARD"
echo "    MODEL     = $MODEL"
echo "    PWGPY     = $PWGPY"
echo

# # Go up to Make_gridpacks; test if genproductions is properly setup
cd $MAKEDIR
source Set_genproductions.sh


########################################
# Clear up old files if they exist
########################################

echo "Clearing files from previous run (if present) ..."
cd $CMSSW_VERSION/src/genproductions/bin/Powheg
rm -rf $RUNNAME
rm -rf run_full_$RUNNAME.sh
rm -rf run_full_RUNNAME.log
rm -rf $CARDDIR.input
rm -rf RUNNAME_$MODEL.tgz
rm -rf runcmsgrid.sh
cd $MAKEDIR
echo "    Done"

# Copy necessary files to the proper directory
cp input/$RUNNAME/$INPUTCARD $CMSSW_VERSION/src/genproductions/bin/Powheg

cd $CMSSW_VERSION/src/genproductions/bin/Powheg

echo
echo "STARTING ACTUAL GRIDPACK GENERATION"
echo "python $PWGPY -p f -i $INPUTCARD -m $MODEL -f $RUNNAME -n 77"
echo

python $PWGPY -p f -i $INPUTCARD -m $MODEL -f $RUNNAME -n 5000


cd $STARTDIR