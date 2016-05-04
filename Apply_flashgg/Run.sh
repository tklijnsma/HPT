
# Set path to showered root files
cd ../Run_gridpacks_and_shower/Saved_root_files/
export SHOWEREDROOTPATH=$(pwd)
cd -

if [ $# -eq 0 ]; then
    echo "    No arguments supplied"
    echo "    Supply the name of one of the following directories:"
    ls $SHOWEREDROOTPATH
    return 1
fi

# Fill in the root file to use
export RUNNAME="$1"


# First make sure flashgg is setup
source Set_flashgg.sh

# CMSSW project directory from which cmsRun will be ran
TESTDIR=$CMSSW_VERSION/src/flashgg/MicroAOD/test/


echo "Making the configuration using Scripts/Make_hgg_gen_analysis.py"
python Scripts/Make_hgg_gen_analysis.py $RUNNAME > $TESTDIR/cfg_$RUNNAME.py

echo "Entering $TESTDIR"
cd $TESTDIR

echo "Starting the run: cmsRun cfg_$RUNNAME.py"
cmsRun cfg_$RUNNAME.py

cd $FLASHBASE

mv $TESTDIR/output.root $FLASHBASE/flashgg_$RUNNAME.root