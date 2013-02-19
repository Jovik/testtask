#!/bin/bash

# Get VLC version from path
VLC_VER=`basename $1`

# Delete old log file
LOG_FILE="."$VLC_VER".txt"
rm $LOG_FILE

# Redirect standard output to the log file
exec 1>$LOG_FILE

# Get all folders and execute gcov in every one of it
for folder in $(find $1 -type d -exec bash -c "cd '{}' && pwd" \;)
do
    ( cd $folder ; gcov `find . -name '*.gcda'` )
done
