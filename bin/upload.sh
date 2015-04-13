#!/bin/bash

echo 'Available PyPI servers on your ~/.pypirc:'
python bin/pypi-servers.py
echo

read -r -p "Choose PyPI index-server: " PYPI_SERVER
echo python setup.py -q sdist upload -r "$PYPI_SERVER"
