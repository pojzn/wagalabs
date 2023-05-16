@echo off

for /f "delims=" %%i in ('python.exe --version') do set PYTHON_VERSION=%%i

set VENV_DIR=..\venv
echo %PYTHON_VERSION%
IF "%PYTHON_VERSION%" == "Python 3.11.3" (
    echo "Clearing previous and creating new virtual environment."
    python -m venv --clear %VENV_DIR%

    echo "Activating virtual environment."
    %VENV_DIR%\Scripts\activate.bat

    echo "Upgrading PIP."
    python -m pip install --upgrade pip

    echo "Installing requirements."
    pip install -r requirements.txt

    echo.

    python -m pytest ..\tests

    echo.
    echo "*********"
    echo "* Done! *"
    echo "*********"
    deactivate
) ELSE (
    echo "***************************************************************************"
    echo "* Python version 3.11.3 is not installed or not found in the PATH env var."
    echo "* Please install Python version 3.11.3 (amd64 arch) from"
    echo "* https://www.python.org/ftp/python/3.11.3/python-3.11.3-amd64.exe"
    echo "***************************************************************************"
)