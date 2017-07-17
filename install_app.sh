# #!/bin/bash

# ## Install de usershub

# #cp settings.ini.sample settings.ini

nano settings.ini

. ./settings.ini

if [ "$(id -u)" == "0" ]; then
   echo -e "\e[91m\e[1mThis script should NOT be run as root\e[0m" >&2
   echo -e "\e[91m\e[1mLancez ce script avec l'utilisateur courant : '$monuser'\e[0m" >&2
   exit 1
fi

function database_exists () {
    # /!\ Will return false if psql can't list database. Edit your pg_hba.conf
    # as appropriate.
    if [ -z $1 ]
        then
        # Argument is null
        return 0
    else
        # Grep db name in the list of database
        sudo -n -u postgres -s -- psql -tAl | grep -q "^$1|"
        return $?
    fi
}



echo "Instalation de l'environnement logiciel..."
#Instalation environnement PHP 
sudo apt-get -y purge `dpkg -l | grep php| awk '{print $2}' |tr "\n" " "`

sudo add-apt-repository ppa:ondrej/php

sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get install -y php5.6

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

sudo apt-get install -y tofrodos
sudo ln -s /usr/bin/fromdos /usr/bin/dos2unix 


echo "Création des utilisateurs postgreSQL..."
sudo -n -u postgres -s psql -c "CREATE ROLE $user_pg WITH LOGIN PASSWORD '$user_pg_pass';"
sudo -n -u postgres -s psql -c "CREATE ROLE $user_atlas WITH LOGIN PASSWORD '$user_atlas_pass';"
#sudo -n -u postgres -s psql -c "CREATE ROLE $admin_pg WITH SUPERUSER LOGIN PASSWORD '$admin_pg_pass';" 




# # Installation de UsersHub avec l'utilisateur courant
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
echo "            \"dbfunname\":\"BDN\"" >> config/dbconnexions.json 
echo "            ,\"host\":\"$pg_host\"" >> config/dbconnexions.json 
echo "            ,\"dbname\":\"$bdn_db_name\"" >> config/dbconnexions.json 
echo "            ,\"user\":\"$user_pg\"" >> config/dbconnexions.json 
echo "            ,\"pass\":\"$user_pg_pass\"" >> config/dbconnexions.json 
echo "            ,\"port\":\"$pg_port\"" >> config/dbconnexions.json 
echo "        }" >> config/dbconnexions.json  
echo "    ]" >> config/dbconnexions.json
echo "}" >> config/dbconnexions.json


# ## creation de la vue pour utilisation des utiliateurs dans toutes les applications

# # export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/usershub.sql  &>> log/install_db.log
# # export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/create_view_utilisateurs.sql  &>> log/install_db.log



# #Instalation de BDN


# ##INSTAL des dependances python
# # virtualenv ./venv
# # . ./venv/bin/activate
# # pip install -r requirements.txt

if database_exists $bdn_db_name
then
        if $drop_bdn_db
            then
            echo "Suppression de la BDD..."
            sudo -n -u postgres -s dropdb $bdn_db_name  &>> logs/install_db.log
        else
            echo "La base de données existe et le fichier de settings indique de ne pas la supprimer."
        fi
fi

# # Sinon je créé la BDD
if ! database_exists $bdn_db_name 
then
  
echo "Création de la BDD..."

  sudo -u postgres psql -c "CREATE USER $user_pg WITH PASSWORD '$user_pg_pass'"

  sudo -n -u postgres -s createdb -O $user_pg $bdn_db_name

  echo "Ajout de postGIS et pgSQL à la base de données"
  sudo -n -u postgres -s psql -d $bdn_db_name -c "CREATE EXTENSION IF NOT EXISTS postgis;"

  sudo -n -u postgres -s psql -d $bdn_db_name -c "CREATE SCHEMA contact_flore AUTHORIZATION $user_pg;"
  sudo -n -u postgres -s psql -d $bdn_db_name -c "CREATE SCHEMA contact_faune AUTHORIZATION $user_pg;"
  sudo -n -u postgres -s psql -d $bdn_db_name -c "CREATE SCHEMA synthese AUTHORIZATION $user_pg;"
  #sudo -n -u postgres -s psql -d $bdn_db_name -c "CREATE SCHEMA taxonomie AUTHORIZATION $user_pg;"
  sudo -n -u postgres -s psql -d $bdn_db_name -c "CREATE SCHEMA layers AUTHORIZATION $user_pg;"
  sudo -n -u postgres -s psql -d $bdn_db_name -c "CREATE SCHEMA fdw AUTHORIZATION $user_pg;"
  sudo -n -u postgres -s psql -d $bdn_db_name -c "CREATE SCHEMA utilisateur AUTHORIZATION $user_pg;"
fi




# ##################################
# ### INSTALATION DE TAXHUB ########
# ##################################

# # Installation de TaxHub avec l'utilisateur courant
echo "Téléchargement et installation de TaxHub ..."
cd /tmp
wget https://github.com/PnX-SI/TaxHub/archive/$taxhub_release.zip
unzip $taxhub_release.zip
rm $taxhub_release.zip
mv TaxHub-$taxhub_release /home/$monuser/taxhub/
cd /home/$monuser/taxhub

# # Configuration des settings de TaxHub
echo "Configuration de l'application TaxHub ..."
cp settings.ini.sample settings.ini
sed -i "s/drop_apps_db=.*$/drop_apps_db=false/g" settings.ini
sed -i "s/db_host=.*$/db_host=$pg_host/g" settings.ini
sed -i "s/db_port=.*$/db_port=$pg_port/g" settings.ini
sed -i "s/db_name=.*$/db_name=$bdn_db_name/g" settings.ini
sed -i "s/user_pg=.*$/user_pg=$user_pg/g" settings.ini
sed -i "s/user_pg_pass=.*$/user_pg_pass=$user_pg_pass/g" settings.ini
sed -i "s/user_schema=.*$/user_schema=local/g" settings.ini
sed -i "s/usershub_host=.*$/usershub_host=$pg_host/g" settings.ini
sed -i "s/usershub_port=.*$/usershub_port=$pg_port/g" settings.ini
sed -i "s/usershub_db=.*$/usershub_db=$usershubdb_name/g" settings.ini
sed -i "s/usershub_user=.*$/usershub_user=$user_pg/g" settings.ini
sed -i "s/usershub_pass=.*$/usershub_pass=$user_pg_pass/g" settings.ini




# # Configuration Apache de TaxHub
sudo touch /etc/apache2/sites-available/taxhub.conf
sudo sh -c 'echo "# Configuration TaxHub" >> /etc/apache2/sites-available/taxhub.conf'
#sudo sh -c 'echo "RewriteEngine  on" >> /etc/apache2/sites-available/taxhub.conf'
#sudo sh -c 'echo "RewriteRule    \"taxhub$\"  \"taxhub/\"  [R]" >> /etc/apache2/sites-available/taxhub.conf'
sudo sh -c 'echo "<Location /taxhub>" >> /etc/apache2/sites-available/taxhub.conf'
sudo sh -c 'echo "ProxyPass  http://127.0.0.1:8000/ retry=0" >> /etc/apache2/sites-available/taxhub.conf'
sudo sh -c 'echo "ProxyPassReverse  http://127.0.0.1:8000/" >> /etc/apache2/sites-available/taxhub.conf'
sudo sh -c 'echo "</Location>" >> /etc/apache2/sites-available/taxhub.conf'
sudo sh -c 'echo "#FIN Configuration TaxHub" >> /etc/apache2/sites-available/taxhub.conf'

sudo sed -i "s/<\/VirtualHost>//g" /etc/apache2/sites-available/000-default.conf
sudo sed -i "s/# vim.*$//g" /etc/apache2/sites-available/000-default.conf
sudo sh -c 'echo "# Configuration TaxHub - ne fonctionne pas dans le 000-default.conf" >> /etc/apache2/sites-available/000-default.conf'
sudo sh -c 'echo "RewriteEngine  on" >> /etc/apache2/sites-available/000-default.conf'
sudo sh -c 'echo "RewriteRule    \"taxhub$\"  \"taxhub/\"  [R]" >> /etc/apache2/sites-available/000-default.conf'
sudo sh -c 'echo "</VirtualHost>" >> /etc/apache2/sites-available/000-default.conf'
sudo sh -c 'echo "" >> /etc/apache2/sites-available/000-default.conf'
sudo sh -c 'echo "# vim: syntax=apache ts=4 sw=4 sts=4 sr noet" >> /etc/apache2/sites-available/000-default.conf'

sudo a2ensite taxhub
sudo a2enmod proxy
sudo a2enmod proxy_http

#Probleme avec le mod_rewrite
sudo ls -l /usr/lib/apache2/modules/mod_rewrite.so
sudo echo "LoadModule rewrite_module /usr/lib/apache2/modules/mod_rewrite.so" > /etc/apache2/mods-available/rewrite.load
sudo a2enmod rewriteEnabling module rewrite
sudo service apache2 restart

# Installation et configuration de l'application TaxHub
./install_app.sh
# sudo apache2ctl restart


## installation du schema taxonomie


echo "Décompression des fichiers du taxref..."
cd data/inpn
unzip -o TAXREF_INPN_v9.0.zip -d /tmp
unzip -o ESPECES_REGLEMENTEES.zip -d /tmp
unzip -o LR_FRANCE.zip -d /tmp

cd ../..


echo "Création du schéma taxonomie..."
echo "" &>> logs/install_db.log
echo "" &>> logs/install_db.log
echo "--------------------" &>> logs/install_db.log
echo "Création du schéma taxonomie" &>> logs/install_db.log
echo "--------------------" &>> logs/install_db.log
echo "" &>> logs/install_db.log
export PGPASSWORD=$user_pg_pass;psql -h $pg_host -U $user_pg -d $bdn_db_name -f data/taxhubdb.sql  &>> logs/install_db.log

echo "Insertion  des données taxonomiques de l'inpn... (cette opération peut être longue)"
echo "" &>> logs/install_db.log
echo "" &>> logs/install_db.log
echo "--------------------" &>> logs/install_db.log
echo "Insertion  des données taxonomiques de l'inpn" &>> logs/install_db.log
echo "--------------------" &>> logs/install_db.log
echo "" &>> logs/install_db.log
sudo -n -u postgres -s psql -d $bdn_db_name -f data/inpn/data_inpn_v9_taxhub.sql &>> logs/install_db.log

echo "Création des données dictionnaires du schéma taxonomie..."
echo "" &>> logs/install_db.log
echo "" &>> logs/install_db.log
echo "--------------------" &>> logs/install_db.log
echo "Création des données dictionnaires du schéma taxonomie" &>> logs/install_db.log
echo "--------------------" &>> logs/install_db.log
echo "" &>> logs/install_db.log
export PGPASSWORD=$user_pg_pass;psql -h $pg_host -U $user_pg -d $bdn_db_name -f data/taxhubdata.sql  &>> logs/install_db.log

echo "Insertion d'un jeu de taxons exemples dans le schéma taxonomie..."
echo "" &>> logs/install_db.log
echo "" &>> logs/install_db.log
echo "--------------------" &>> logs/install_db.log
echo "Insertion d'un jeu de taxons exemples dans le schéma taxonomie" &>> logs/install_db.log
echo "--------------------" &>> logs/install_db.log
echo "" &>> logs/install_db.log
export PGPASSWORD=$user_pg_pass;psql -h $pg_host -U $user_pg -d $bdn_db_name -f data/taxhubdata_taxon_example.sql  &>> logs/install_db.log

echo "Création de la vue représentant la hierarchie taxonomique..."
echo "" &>> logs/install_db.log
echo "" &>> logs/install_db.log
echo "--------------------" &>> logs/install_db.log
echo "Création de la vue représentant la hierarchie taxonomique" &>> logs/install_db.log
echo "--------------------" &>> logs/install_db.log
echo "" &>> logs/install_db.log
export PGPASSWORD=$user_pg_pass;psql -h $pg_host -U $user_pg -d $bdn_db_name -f data/vm_hierarchie_taxo.sql  &>> logs/install_db.log
