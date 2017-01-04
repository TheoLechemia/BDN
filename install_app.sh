#!/bin/bash


if [ "$(id -u)" == "0" ]; then
   echo -e "\e[91m\e[1mThis script should NOT be run as root\e[0m" >&2
   exit 1
fi

sudo apt-get update
sudo apt-get -y upgrade

sudo apt-get install -y unzip
sudo apt-get install -y apache2
sudo apt-get install -y libapache2-mod-wsgi
sudo apachectl restart

sudo apt-get install -y postgresql postgis
sudo apt-get install -y python-setuptools
sudo apt-get install -y libpq-dev python-dev


sudo apt-get install -y python python-pip
sudo apt-get install -y python-gdal
sudo apt-get install -y gdal-bin

sudo apt-get install -y python-virtualenv

sudo apt-get install tofrodos
sudo ln -s /usr/bin/fromdos /usr/bin/dos2unix 



#install python packages

virtualenv ./venv
. ./venv/bin/activate
pip install -r requirements.txt
