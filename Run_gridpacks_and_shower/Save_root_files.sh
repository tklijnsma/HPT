if [ -z "$1" ]; then
    return 0
elif [ ! -d "$1" ]; then
    return 0
else
    RUNNAME="$1"
fi

DATESTAMP="$(date +'%m%d')"

mkdir -p Saved_root_files/$DATESTAMP_$RUNNAME
cp $RUNNAME/*.root Saved_root_files/$DATESTAMP_$RUNNAME/