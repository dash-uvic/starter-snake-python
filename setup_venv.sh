#!/bin/bash

env_name="$1"
py_ver=$2

if [ -z "$env_name" ]; then
    echo "Usage: need virtualenv name"
fi

if [ -z "$py_ver" ]; then
    echo "Using python3"
    py_ver=python3
fi

$py_ver -m virtualenv $env_name
source $env_name/bin/activate

pip install --upgrade pip

if [ -e requirements.txt ]; then
    pip install -r requirements.txt
fi
