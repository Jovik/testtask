#!/bin/bash

LOG_FILE=".install_log.txt"
rm $LOG_FILE

shopt -s expand_aliases
alias log="tee -a $LOG_FILE"

assert () {
    echo -n $3 | log
    if [ $1 -ne $2 ] ; then
        echo " failed!" | log
        echo "Check log (install_log.txt) file for details"
        exit 1
    fi
    echo " passed" | log
}

echo "Please provide root password for apt-get\n"

echo "Updating system:"
sudo apt-get --quiet=1 --yes update | log
assert $? 0 "Updating repository..."
sudo apt-get --quiet=1 --yes upgrade | log
assert $? 0 "Updating system..."

echo "Instal required software:"
sudo apt-get --yes install valgrind libavcodec-dev libavformat-dev libswscale-dev libxcb1-dev libxcb-shm0-dev libxcb-xv0-dev libx11-xcb-dev libgl1-mesa-dev libqt4-dev libgcrypt11-dev g++ libpulse-dev libasound2-dev libxcb-composite0-dev python-matplotlib python-flask python-psutil pep8 pylint sqlite3 git | log
assert $? 0 "Installing additional packages..."

echo "Add execute permission to script files:"
sudo chmod a+x core/gcov.sh
assert $? 0 "Successfully changed scripts permission..."
