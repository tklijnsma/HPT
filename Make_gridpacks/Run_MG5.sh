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
    MODEL="$(sed -e '/^[ ]*#/d' -e '/^$/d' $MODELCARD | cat )"
fi

########################################
# Set the MODEL (there should be a MODEL.txt file)
########################################


echo "------------------------------------------------------------------"
echo "Starting a run using MadGraph5"
echo "    RUNNAME    = $RUNNAME"
echo "    RUNCARD    = $RUNCARD"
echo "    PROCCARD   = $PROCCARD"

if [ $EXTRAMODEL = true ]; then
    echo "    EXTRAMODEL = $MODEL"
fi
echo

# # Go up to Make_gridpacks; test if genproductions is properly setup
cd $MAKEDIR
source Set_genproductions.sh

# Set the external model dir (used in gridpack_generation.sh)
export EXTERNALMODELDIR="$(pwd)/input_MG5/externalmodels/"

########################################
# Clear up old files if they exist
########################################

MG5DIR=$CMSSW_VERSION/src/genproductions/bin/MadGraph5_aMCatNLO

echo "Clearing files from previous run (if present) ..."
cd $MG5DIR
rm -rf $RUNNAME
rm -rf RUNNAME.log
cd $MAKEDIR
echo "    Done"


echo "Entering $MG5DIR"
cd $MG5DIR

# Make a temporary card dir in the MG5 directory
#   This should be a relative directory
TEMPCARDDIR="tempcards/$RUNNAME"
mkdir -p $TEMPCARDDIR

# Copy necessary files to the proper directory
cp $MAKEDIR/input_MG5/$RUNNAME/* $TEMPCARDDIR/

ls $TEMPCARDDIR

echo
echo "STARTING ACTUAL GRIDPACK GENERATION"
echo "./gridpack_generation.sh $RUNNAME $TEMPCARDDIR 1nd"
echo

./gridpack_generation.sh $RUNNAME $TEMPCARDDIR 1nd
#./gridpack_generation.sh $RUNNAME cards/production/13TeV/higgs/ggh012j_5f_LO_FXFX_125/ 2nd
#python $PWGPY -p f -i $INPUTCARD -m $MODEL -f $RUNNAME -n 5000

cd $STARTDIR