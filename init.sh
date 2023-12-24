#!/bin/bash

#installing python3 and pip3
sudo apt update

function setupPython3 {
    if ! python3 -V &> /dev/null; then
        echo "Installing python3"
        sudo apt install python3 -y
    fi
    if ! pip3 -V &> /dev/null; then
        echo "Installing pip3"
        sudo apt install python3-pip -y
    fi
}

setupPython3 

# This script is used to install all the python dependencies needed for the project
function installIfNotInstalled {
    for denependency in "$@"; do
        if ! python -c "import $denependency" &> /dev/null; then
            echo "Installing $denependency"
            pip install $denependency
        fi
        else
            echo "$denependency is already installed"
        fi
    done
}

installIfNotInstalled os ssl json datetime configparser