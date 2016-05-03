# Setup CMSSW
source Set_CMSSW.sh

GITREPO="https://github.com/cms-analysis/flashgg.git"

echo "Setting up flashgg"

# Go to /src
echo "    Entering $CMSSW_VERSION/src"
cd $CMSSW_VERSION/src


# If "renew" flag is passed, delete existing flashgg
if [ $# -eq 0 ]; then
    echo "    No arguments supplied"
elif [ "$1" = "renew" ] && [ -r flashgg ]; then
    echo "    Found existing flashgg directory; Deleting it and remaking"
    rm -rf flashgg
elif [ "$1" = "recompile" ] && [ -r flashgg ]; then
    RECOMPILE="TRUE"
fi

# Get the flashgg repo if necessary
if [ -r "flashgg" ]; then
    echo "    flashgg already exists in ${CMSSW_VERSION}/src"
else
    echo "    Setting up fresh flashgg from $GITREPO"
    git cms-init
    git clone $GITREPO
    RECOMPILE="TRUE"
fi

# Setup script
echo "Running setup script"
source flashgg/setup.sh

# Copy in necessary files
cp ../../Scripts/DummyVertexProducer.cc flashgg/MicroAOD/plugins/

if [ ! -z "$RECOMPILE" ]; then
    # Compile
    echo "Compiling"
    scram b -j 9
fi

cd ../..