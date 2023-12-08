#!/bin/bash

# setup the barbie drive in 
echo "Install python dependencies"
pip install -r requirements.txt

# setup the services
echo "Setting up services"
./setup_service.sh web_app
