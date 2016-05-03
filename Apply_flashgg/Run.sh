# First make sure flashgg is setup
source Set_flashgg.sh

# CMSSW project directory from which cmsRun will be ran
TESTDIR=$CMSSW_VERSION/src/flashgg/MicroAOD/test/

# Set path to showered root files
cd ../Run_gridpacks_and_shower/Saved_root_files/
export SHOWEREDROOTPATH=$(pwd)
cd -

# Fill in the root file to use
export RUNNAME="$1"

echo "Making the configuration using Scripts/Make_hgg_gen_analysis.py"
python Scripts/Make_hgg_gen_analysis.py $RUNNAME > $TESTDIR/hgg_gen_analysis.py

echo "Entering $TESTDIR"
cd $TESTDIR

echo "Starting the run"
cmsRun hgg_gen_analysis.py

cd $FLASHBASE

mv $TESTDIR/output.root $FLASHBASE/flashgg_$RUNNAME.root