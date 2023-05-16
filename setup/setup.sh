#!/bin/bash

# Get Python version string.
python_version=$(python --version)

# Define directory where virtual environment will be placed.
VENV_DIR=../venv
if [ "$python_version" = "Python 3.11.3" ]; then
    echo "Clearing previous and creating new virtual environment."
    python -m venv --clear $VENV_DIR

    echo "Activating virtual environment."
    . $VENV_DIR/bin/activate

    echo "Upgrading PIP."
    $VENV_DIR/bin/python -m pip install --upgrade pip

    echo "Installing requirements."
    $VENV_DIR/bin/pip install -r requirements.txt

    echo.
    python -m pytest ../tests

    echo.
    echo "*********"
    echo "* Done! *"
    echo "*********"
    deactivate

else
    echo "***************************************************************************"
    echo "* Python version 3.11.3 is not installed or not found in the PATH env var."
    echo "* Please install Python version 3.11.3 (amd64 arch)."
    echo "* Depending on your distro, the installation steps may vary."
    echo "* https://tecadmin.net/how-to-install-python-3-11-on-ubuntu/"
    echo "***************************************************************************"
fi