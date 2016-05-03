# Setup CMSSW
source Set_CMSSW.sh

GITREPO="https://github.com/tklijnsma/genproductions.git"


echo "Setting up genproductions"

# Go to /src
echo "    Entering $CMSSW_VERSION/src"
cd $CMSSW_VERSION/src

if [ -r "genproductions" ]; then
    echo "    genproductions already exists in ${CMSSW_VERSION}/src"
else
    echo "    Setting up fresh genproductions from $GITREPO"
    git clone $GITREPO
fi

cd ../..