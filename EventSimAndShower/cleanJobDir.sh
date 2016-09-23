cleanJobDir_startDir="$(pwd)"

JOBDIR="$1"

if [ ! -d $JOBDIR ]; then
    echo "Error: $JOBDIR is not a directory"
    return
fi

# Enter src directory
cd $JOBDIR
cd "$(ls)"
cd src

echo "Removing cfg and root files in $(pwd)"
rm *_cfg*.py
rm *.root
rm -rf cfg*

echo
echo "Contents now:"
ls
echo

cd $cleanJobDir_startDir