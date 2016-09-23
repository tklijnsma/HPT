#!/bin/bash

# Set some common variables
. setJobEnv.sh

collect_startDir=$(pwd)


if [ $# -eq 0 ]; then
    echo "Supply the name of directory in which to look for root files"
    return 1
fi

DIR="$1"

if [ ! -d $DIR ]; then
    echo "Error: $DIR is not a directory"
    return 1
fi

# Check if test flag is passed
TESTFLAG="$2"
TESTMODE="False"
if [ ! -z $TESTFLAG ]; then
    if [ "$TESTFLAG" = "TEST" ]; then
        echo "TESTMODE ACTIVATED"
        TESTMODE="True"
    fi
fi


# Open up a collection directory
TIMESTAMP=$(date +%m%d)
COLLECTIONDIR="$(fullpath RootOutput/${TIMESTAMP}_$DIR)"
mkdir -p $COLLECTIONDIR


cd $DIR/$CMSSW_VERSION/src

for cfgdir in cfg* ; do
    if [ $TESTMODE = "True" ]; then
        echo "Would now do: mv $cfgdir/*.root $COLLECTIONDIR/"
    else
        echo "DOING: mv $cfgdir/*.root $COLLECTIONDIR/"
        mv $cfgdir/*.root $COLLECTIONDIR/
    fi
done

echo "Moved all root files to $COLLECTIONDIR"
echo "Files now in $COLLECTIONDIR:"
cd $COLLECTIONDIR
ls


cd $collect_startDir
echo "End of collection script"