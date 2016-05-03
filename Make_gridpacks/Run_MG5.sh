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
    ls input_MG5
    return 1
fi

RUNNAME="$1"

########################################
# Check if there is an input card
########################################

PROCCARD="input_MG5/${RUNNAME}/${RUNNAME}_proc_card.dat"

# If no proc card found
if [ ! -f "$PROCCARD" ]; then
    echo "Could not find a proc card in input_MG5/$RUNNAME"
    cd $STARTDIR
    return 
fi


RUNCARD="input_MG5/${RUNNAME}/${RUNNAME}_run_card.dat"

# If no run card found
if [ ! -f "$RUNCARD" ]; then
    echo "Could not find a run card in input_MG5/$RUNNAME"
    cd $STARTDIR
    return 
fi


MODELCARD="input_MG5/${RUNNAME}/${RUNNAME}_extramodels.dat"

# If no extramodels card found
if [ ! -f "$MODELCARD" ]; then
    echo "Could not find an extramodels card in input_MG5/$RUNNAME"
    EXTRAMODEL=false
else
    EXTRAMODEL=true
fi

########################################
# Set the MODEL (there should be a MODEL.txt file)
########################################


echo "------------------------------------------------------------------"
echo "Starting a run using MadGraph5"
echo "    RUNNAME   = $RUNNAME"
echo "    RUNCARD   = $RUNCARD"
echo "    PROCCARD  = $PROCCARD"

if [ $EXTRAMODEL = true ]; then
    echo "    EXTRAMODEL = $(sed -e '/^[ ]*#/d' -e '/^$/d' $MODELCARD | cat )"
fi
echo

return 1

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