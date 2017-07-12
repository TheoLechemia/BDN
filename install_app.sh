#!/bin/bash

cp ./Apps/config.py.sample ./Apps/config.py

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




## Install de usershub

sudo apt-get purge `dpkg -l | grep php| awk '{print $2}' |tr "\n" " "`

sudo add-apt-repository ppa:ondrej/php

sudo apt-get update
sudo apt-get install php5.6

sudo apt-get install -y libapache2-mod-php5.6
sudo apt-get install -y libapache2-mod-wsgi
sudo apt-get install -y php5.6-pgsql
