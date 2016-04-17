#!/bin/bash

pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd -P`
popd > /dev/null

mkdir -p $SCRIPTPATH/data

if [ ! -e $SCRIPTPATH/venv/ ]; then
    python3 -m venv $SCRIPTPATH/venv
fi

$SCRIPTPATH/venv/bin/pip3 install -r $SCRIPTPATH/requirements.txt