# Setup CMSSW
source Set_CMSSW.sh

GITREPO="https://github.com/cms-analysis/flashgg.git"

echo "Setting up flashgg"

# Go to /src
echo "    Entering $CMSSW_VERSION/src"
cd $CMSSW_VERSION/src


RECOMPILE=false

# If "renew" flag is passed, delete existing flashgg
if [ $# -eq 0 ]; then
    echo "    No arguments supplied"
elif [ "$1" = "renew" ] && [ -r flashgg ]; then
    echo "    Found existing flashgg directory; Deleting it and remaking"
    rm -rf flashgg
elif [ "$1" = "recompile" ] && [ -r flashgg ]; then
    RECOMPILE=true
fi

# Get the flashgg repo if necessary
if [ -r "flashgg" ]; then
    echo "    flashgg already exists in ${CMSSW_VERSION}/src"
else
    echo "    Setting up fresh flashgg from $GITREPO"
    git cms-init
    git clone $GITREPO
    # git checkout 2d121446d4d7972ac0d0c43de03f11a0b8afe4c9
    git checkout 63f87406b0c68300d3b9576e1e77ba1ddd89cf72
    RECOMPILE=true
fi

# Setup script
echo "Running setup script"
source flashgg/setup.sh

# Copy in necessary files
cp ../../Scripts/DummyVertexProducer.cc flashgg/MicroAOD/plugins/

if [ $RECOMPILE = true ]; then
    # Compile
    echo "Compiling"
    scram b -j 9
fi

cd ../..