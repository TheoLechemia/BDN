#!/bin/bash

## Install de usershub

cp settings.ini.sample settings.ini

nano settings.ini

if [ "$(id -u)" == "0" ]; then
   echo -e "\e[91m\e[1mThis script should NOT be run as root\e[0m" >&2
   echo -e "\e[91m\e[1mLancez ce script avec l'utilisateur courant : '$monuser'\e[0m" >&2
   exit 1
fi



echo "Instalation de l'environnement logiciel..."
#Instalation environnement PHP 
sudo apt-get purge `dpkg -l | grep php| awk '{print $2}' |tr "\n" " "`

sudo add-apt-repository ppa:ondrej/php

sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get install php5.6

sudo apt-get install -y libapache2-mod-php5.6
sudo apt-get install -y libapache2-mod-wsgi
sudo apt-get install -y php5.6-pgsql


#Instalation environnement Python 

sudo apt-get update


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


echo "Création des utilisateurs postgreSQL..."
sudo -n -u postgres -s psql -c "CREATE ROLE $user_pg WITH LOGIN PASSWORD '$user_pg_pass';"
sudo -n -u postgres -s psql -c "CREATE ROLE $user_atlas WITH LOGIN PASSWORD '$user_atlas_pass';"
#sudo -n -u postgres -s psql -c "CREATE ROLE $admin_pg WITH SUPERUSER LOGIN PASSWORD '$admin_pg_pass';" 




# Installation de UsersHub avec l'utilisateur courant
echo "téléchargement et installation de UsersHub ..."
cd /tmp
wget https://github.com/PnEcrins/UsersHub/archive/$usershub_release.zip
unzip $usershub_release.zip
rm $usershub_release.zip
mv UsersHub-$usershub_release /home/$monuser/usershub/
cd /home/$monuser/usershub

# Configuration des settings de UsersHub
echo "Installation de la base de données et configuration de l'application UsersHub ..."
cp config/settings.ini.sample config/settings.ini
sed -i "s/drop_apps_db=.*$/drop_apps_db=$drop_usershubdb/g" config/settings.ini
sed -i "s/db_host=.*$/db_host=$pg_host/g" config/settings.ini
sed -i "s/db_name=.*$/db_name=$usershubdb_name/g" config/settings.ini
sed -i "s/user_pg=.*$/user_pg=$user_pg/g" config/settings.ini
sed -i "s/user_pg_pass=.*$/user_pg_pass=$user_pg_pass/g" config/settings.ini
# Installation de la base de données UsersHub en root
sudo ./install_db.sh
# Installation et configuration de l'application UsersHub
./install_app.sh
# Configuration de la connexion à la base de données GeoNature
rm config/dbconnexions.json
touch config/dbconnexions.json
echo "{" >> config/dbconnexions.json
echo "    \"databases\":" >> config/dbconnexions.json
echo "    [" >> config/dbconnexions.json
echo "        {" >> config/dbconnexions.json  
echo "            \"dbfunname\":\"Utilisateurs\"" >> config/dbconnexions.json 
echo "            ,\"host\":\"$pg_host\"" >> config/dbconnexions.json 
echo "            ,\"dbname\":\"$usershubdb_name\"" >> config/dbconnexions.json 
echo "            ,\"user\":\"$user_pg\"" >> config/dbconnexions.json 
echo "            ,\"pass\":\"$user_pg_pass\"" >> config/dbconnexions.json 
echo "            ,\"port\":\"$pg_port\"" >> config/dbconnexions.json 
echo "        }" >> config/dbconnexions.json
echo "        ,{" >> config/dbconnexions.json
echo "            \"dbfunname\":\"GeoNature\"" >> config/dbconnexions.json 
echo "            ,\"host\":\"$pg_host\"" >> config/dbconnexions.json 
echo "            ,\"dbname\":\"$geonaturedb_name\"" >> config/dbconnexions.json 
echo "            ,\"user\":\"$user_pg\"" >> config/dbconnexions.json 
echo "            ,\"pass\":\"$user_pg_pass\"" >> config/dbconnexions.json 
echo "            ,\"port\":\"$pg_port\"" >> config/dbconnexions.json 
echo "        }" >> config/dbconnexions.json  
echo "    ]" >> config/dbconnexions.json
echo "}" >> config/dbconnexions.json



#Instalation de BDN

# virtualenv ./venv
# . ./venv/bin/activate
# pip install -r requirements.txt























cp ./Apps/config.py.sample ./Apps/config.py
sudo nano ./Apps/config.py








