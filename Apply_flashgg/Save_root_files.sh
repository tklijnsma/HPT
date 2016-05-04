if [ $# -eq 0 ]; then
    echo "    Supply a directory name for the root files to be moved to"
    return 1
fi
SAVENAME=$1

# First (re)create directory for saved root files
mkdir -p Saved_root_files/$SAVENAME

# Move .root files to it
mv *.root Saved_root_files/$SAVENAME/