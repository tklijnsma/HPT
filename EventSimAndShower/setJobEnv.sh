#!/bin/bash

# Small function that returns the full path of a relative path
#   (Don't need to cd back because it's a function)
fullpath() {
    if [ -d $1 ]; then
        echo "$(cd $1 && pwd)"
    else
        echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
    fi
}


# ======================================
# Fixed variables

export SCRAM_ARCH=slc6_amd64_gcc481
export CMSSW_VERSION=CMSSW_7_1_14

# Relative path form src to fragments
export RELATIVE_FRAGMENTDIR=Configuration/GenProduction/python/

export EVENTSIM_FRAGMENT=EventSim_fragment.py
export SHOWER_FRAGMENT=Shower_fragment.py

export X509_USER_PROXY=$HOME/private/personal/voms_proxy.cert

export setJobEnv_dir=$(dirname $( fullpath "${BASH_SOURCE[0]}" ))

source /afs/cern.ch/cms/cmsset_default.sh


# ======================================
# Variables that depend on the tarball

# Small function that takes the path of a tarball, and produces the name of a run
name() {
    echo "$(basename $1 .tgz)"
}

# Small function that takes the path of a tarball, and produces the name of the base directory
basedir() {
    echo "JOBS_$(name $1)"
}


# ======================================
# Functions

# Function to be executed if no tarball was passed, or passed tarball does not exist
function tarball_error {
    echo "No (valid) path to tarball passed"
    TARBALLPATH=$(fullpath "../Make_gridpacks/Saved_tarballs")
    echo "Available tarballs in ${TARBALLPATH}:"
    for tarball in $TARBALLPATH/*.tgz; do echo "    $TARBALLPATH/$(basename $tarball)"; done
    return 1
}
