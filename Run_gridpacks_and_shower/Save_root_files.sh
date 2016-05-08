if [ $# -eq 0 ]; then
    echo "    No arguments supplied"
    echo "    Supply the name of one of the following directories:"
    ls
    return 1
fi

RUNNAME="$1"

DATESTAMP="$(date +'%m%d')"

mkdir -p Saved_root_files/${DATESTAMP}_${RUNNAME}
#cp $RUNNAME/*.root Saved_root_files/${DATESTAMP}_${RUNNAME}/
mv $RUNNAME/*.root Saved_root_files/${DATESTAMP}_${RUNNAME}/