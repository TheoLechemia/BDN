# #!/bin/bash

# ## Install de usershub

#cp settings.ini.sample settings.ini

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



# echo "####################################################################
#       ######## Instalation de l'environnement logiciel... ################
#       #################################################################### " 
# #Instalation environnement PHP 
# sudo apt-get -y purge `dpkg -l | grep php| awk '{print $2}' |tr "\n" " "`

# sudo add-apt-repository ppa:ondrej/php

# sudo apt-get update
# sudo apt-get -y upgrade
# sudo apt-get install -y php5.6

# sudo apt-get install -y libapache2-mod-php5.6
# sudo apt-get install -y libapache2-mod-wsgi
# sudo apt-get install -y php5.6-pgsql


# #Instalation environnement Python 

# sudo apt-get update


# sudo apt-get install -y unzip
# sudo apt-get install -y apache2
# sudo apt-get install -y libapache2-mod-wsgi
# sudo apachectl restart

# sudo apt-get install -y postgresql postgis
# sudo apt-get install -y python-setuptools
# sudo apt-get install -y libpq-dev python-dev

# sudo apt-get install -y npm
# sudo apt-get install -y python python-pip
# sudo apt-get install -y python-gdal
# sudo apt-get install -y gdal-bin

# sudo apt-get install -y python-virtualenv

# sudo apt-get install -y tofrodos
# sudo ln -s /usr/bin/fromdos /usr/bin/dos2unix 


# echo "Création des utilisateurs postgreSQL..."
# sudo -n -u postgres -s psql -c "CREATE ROLE $user_pg WITH LOGIN PASSWORD '$user_pg_pass';"
# sudo -n -u postgres -s psql -c "CREATE ROLE $user_atlas WITH LOGIN PASSWORD '$user_atlas_pass';"



# ######################################################################################################
# ######################################################################################################
# ###################################### INSTALATION DE USERSHUB  ######################################
# ######################################################################################################
# ######################################################################################################




# echo "téléchargement et installation de UsersHub ..."
# cd /tmp
# wget https://github.com/PnEcrins/UsersHub/archive/$usershub_release.zip
# unzip $usershub_release.zip
# rm $usershub_release.zip
# mv UsersHub-$usershub_release /home/$monuser/usershub/
# cd /home/$monuser/usershub

# # Configuration des settings de UsersHub
# echo "Installation de la base de données et configuration de l'application UsersHub ..."
# cp config/settings.ini.sample config/settings.ini
# sed -i "s/drop_apps_db=.*$/drop_apps_db=$drop_usershubdb/g" config/settings.ini
# sed -i "s/db_host=.*$/db_host=$pg_host/g" config/settings.ini
# sed -i "s/db_name=.*$/db_name=$usershubdb_name/g" config/settings.ini
# sed -i "s/user_pg=.*$/user_pg=$user_pg/g" config/settings.ini
# sed -i "s/user_pg_pass=.*$/user_pg_pass=$user_pg_pass/g" config/settings.ini
# # Installation de la base de données UsersHub en root
# sudo ./install_db.sh
# # Installation et configuration de l'application UsersHub
# ./install_app.sh
# # Configuration de la connexion à la base de données GeoNature
# rm config/dbconnexions.json
# touch config/dbconnexions.json
# echo "{" >> config/dbconnexions.json
# echo "    \"databases\":" >> config/dbconnexions.json
# echo "    [" >> config/dbconnexions.json
# echo "        {" >> config/dbconnexions.json  
# echo "            \"dbfunname\":\"Utilisateurs\"" >> config/dbconnexions.json 
# echo "            ,\"host\":\"$pg_host\"" >> config/dbconnexions.json 
# echo "            ,\"dbname\":\"$usershubdb_name\"" >> config/dbconnexions.json 
# echo "            ,\"user\":\"$user_pg\"" >> config/dbconnexions.json 
# echo "            ,\"pass\":\"$user_pg_pass\"" >> config/dbconnexions.json 
# echo "            ,\"port\":\"$pg_port\"" >> config/dbconnexions.json 
# echo "        }" >> config/dbconnexions.json
# echo "        ,{" >> config/dbconnexions.json
# echo "            \"dbfunname\":\"BDN\"" >> config/dbconnexions.json 
# echo "            ,\"host\":\"$pg_host\"" >> config/dbconnexions.json 
# echo "            ,\"dbname\":\"$bdn_db_name\"" >> config/dbconnexions.json 
# echo "            ,\"user\":\"$user_pg\"" >> config/dbconnexions.json 
# echo "            ,\"pass\":\"$user_pg_pass\"" >> config/dbconnexions.json 
# echo "            ,\"port\":\"$pg_port\"" >> config/dbconnexions.json 
# echo "        }" >> config/dbconnexions.json  
# echo "    ]" >> config/dbconnexions.json
# echo "}" >> config/dbconnexions.json


# # ## creation de la vue pour utilisation des utiliateurs dans toutes les applications

#   sudo -n -u postgres -s psql -d $usershubdb_name -c "CREATE OR REPLACE VIEW utilisateurs.v_userslist_forall_applications AS 
#  SELECT r.groupe,
#     r.id_role,
#     r.identifiant,
#     r.nom_role,
#     r.prenom_role,
#     r.desc_role,
#     r.pass,
#     r.email,
#     r.id_organisme,
#     r.organisme,
#     r.id_unite,
#     r.remarques,
#     r.pn,
#     r.session_appli,
#     r.date_insert,
#     r.date_update,
#     cor.id_droit AS id_droit_max,
#     cor.id_application
#    FROM utilisateurs.cor_role_droit_application cor
#      JOIN utilisateurs.t_roles r ON r.id_role = cor.id_role;

# ALTER TABLE utilisateurs.v_userslist_forall_applications
#   OWNER TO $user_pg;"

cd /home/$monuser/BDN

# création de l'application BDN et d'un compte admin pour BDN dans usershub
export PGPASSWORD=$user_pg_pass;psql -h $pg_host -U $user_pg -d $usershubdb_name -f data/usershub/usershub_data.sql  &>> log/install_db.log

######################################################################################################
######################################################################################################
###################################### INSTALATION DE BDN   ##########################################
######################################################################################################
######################################################################################################



#Instalation des dependances python
virtualenv ./venv
. ./venv/bin/activate
pip install -r requirements.txt
deactivate
# Instalation dépendance npm
cd ./Apps/static
npm install
cd ../../

#creation du dossier de telechargement
mkdir Apps/static/uploads
chmod 0777 Apps/static/uploads

# remplissage du config.py a partir des données du settings.ini
cp Apps/config.py.sample Apps/config.py
sed -i -e "s/database_name/$bdn_db_name/g" Apps/config.py
sed -i -e "s/user_name/$user_pg/g" Apps/config.py
sed -i -e "s/my_pass/$user_pg_pass/g" Apps/config.py
sed -i -e "s/localhost/$pg_host/g" Apps/config.py
sed -i -e "s/myport/$pg_port/g" Apps/config.py
sed -i -e "s:MY_URL/$monurl:g" Apps/config.py
sed -i -e "s/-61.5361400/$xcoord/g" Apps/config.py
sed -i -e "s/16.2412500/$ycoord/g" Apps/config.py
sed -i -e "s/32620/$projection/g" Apps/config.py
sed -i -e "s/999999999/$no_application/g" Apps/config.py


nano Apps/config.py

if database_exists $bdn_db_name
then
        if $drop_bdn_db
            then
            echo "Suppression de la BDD..."
            sudo -n -u postgres -s dropdb $bdn_db_name  &>> log/install_db.log
        else
            echo "La base de données existe et le fichier de settings indique de ne pas la supprimer."
        fi
fi

# # Sinon je créé la BDD
if ! database_exists $bdn_db_name 
then
  
echo "Création de la BDD..."
#Instalation de la BDD de BDN - sans le schema taxonomie

  sudo -u postgres psql -c "CREATE USER $user_pg WITH PASSWORD '$user_pg_pass'"

  sudo -n -u postgres -s createdb -O $user_pg $bdn_db_name

  echo "Ajout de postGIS et pgSQL à la base de données"
  sudo -n -u postgres -s psql -d $bdn_db_name -c "CREATE EXTENSION IF NOT EXISTS postgis;"
  sudo -n -u postgres -s psql -d $bdn_db_name -c "CREATE SCHEMA contact_flore AUTHORIZATION $user_pg;"
  sudo -n -u postgres -s psql -d $bdn_db_name -c "CREATE SCHEMA contact_faune AUTHORIZATION $user_pg;"
  sudo -n -u postgres -s psql -d $bdn_db_name -c "CREATE SCHEMA synthese AUTHORIZATION $user_pg;"
  sudo -n -u postgres -s psql -d $bdn_db_name -c "CREATE SCHEMA layers AUTHORIZATION $user_pg;"
  sudo -n -u postgres -s psql -d $bdn_db_name -c "CREATE SCHEMA fdw AUTHORIZATION $user_pg;"
  sudo -n -u postgres -s psql -d $bdn_db_name -c "CREATE SCHEMA utilisateurs AUTHORIZATION $user_pg;"
fi

## FDW pour usershubdb
sudo -u postgres -s psql -d $bdn_db_name -c "CREATE EXTENSION IF NOT EXISTS postgres_fdw;"
sudo -u postgres -s psql -d $bdn_db_name -c "CREATE SERVER server_usershubdb FOREIGN DATA WRAPPER postgres_fdw OPTIONS (host '$pg_host', dbname '$usershubdb_name', port '$pg_port');"
sudo -u postgres -s psql -d $bdn_db_name -c "GRANT USAGE ON FOREIGN SERVER server_usershubdb to $user_pg;"
export PGPASSWORD=$user_pg_pass;psql -d bdn -U $user_pg -h $pg_host -c "CREATE USER MAPPING FOR $user_pg SERVER server_usershubdb OPTIONS (user '$user_pg', password '$user_pg_pass');"

cd /home/$monuser/BDN
export PGPASSWORD=$user_pg_pass;psql -h $pg_host -U $user_pg -d $bdn_db_name -f data/fdw_usershub.sql  &>> log/install_db.log




# ######################################################################################################
# ######################################################################################################
# ###################################### INSTALATION DE TAXHUB #########################################
# ######################################################################################################
# ######################################################################################################

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




###### Configuration Apache de TaxHub
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

######Probleme avec le mod_rewrite
sudo ls -l /usr/lib/apache2/modules/mod_rewrite.so
sudo echo "LoadModule rewrite_module /usr/lib/apache2/modules/mod_rewrite.so" > /etc/apache2/mods-available/rewrite.load
sudo a2enmod rewriteEnabling module rewrite
sudo service apache2 restart

###### Installation et configuration de l'application TaxHub
./install_app.sh
sudo apache2ctl restart


## installation du schema taxonomie


echo "Décompression des fichiers du taxref..."
cd data/inpn
unzip -o LR_FRANCE.zip -d /tmp

cd ../..


##### on va dans le dossier BDN pour l'installation de taxref V10
cd /home/$monuser/BDN

unzip -o ./data/taxref.zip -d /tmp
cp ./data/PROTECTION_ESPECES_10.txt /tmp
cp ./data/Liste_rouge_regionale.csv /tmp
cp ./data/PROTECTION_ESPECES_TYPES_10.txt /tmp

echo "Création du schéma taxonomie..."
echo "" &>> log/install_db.log
echo "" &>> log/install_db.log
echo "--------------------" &>> log/install_db.log
echo "Création du schéma taxonomie" &>> log/install_db.log
echo "--------------------" &>> log/install_db.log
echo "" &>> log/install_db.log
export PGPASSWORD=$user_pg_pass;psql -h $pg_host -U $user_pg -d $bdn_db_name -f data/taxhubdb.sql  &>> log/install_db.log


echo "Insertion  des données taxonomiques de l'inpn... (cette opération peut être longue)"
echo "" &>> log/install_db.log
echo "" &>> log/install_db.log
echo "--------------------" &>> log/install_db.log
echo "Insertion  des données taxonomiques de l'inpn" &>> log/install_db.log
echo "--------------------" &>> log/install_db.log
echo "" &>> log/install_db.log
sudo -n -u postgres -s psql -d $bdn_db_name -f data/create_taxref_v10.sql &>> log/install_db.log

#### on retourne dans taxhub pour le reste
cd /home/$monuser/taxhub
echo "Création des données dictionnaires du schéma taxonomie..."
echo "" &>> logs/install_db.log
echo "" &>> logs/install_db.log
echo "--------------------" &>> logs/install_db.log
echo "Création des données dictionnaires du schéma taxonomie" &>> logs/install_db.log
echo "--------------------" &>> logs/install_db.log
echo "" &>> logs/install_db.log
export PGPASSWORD=$user_pg_pass;psql -h $pg_host -U $user_pg -d $bdn_db_name -f data/taxhubdata.sql  &>> logs/install_db.log


echo "Création de la vue représentant la hierarchie taxonomique..."
echo "" &>> logs/install_db.log
echo "" &>> logs/install_db.log
echo "--------------------" &>> logs/install_db.log
echo "Création de la vue représentant la hierarchie taxonomique" &>> logs/install_db.log
echo "--------------------" &>> logs/install_db.log
echo "" &>> logs/install_db.log
export PGPASSWORD=$user_pg_pass;psql -h $pg_host -U $user_pg -d $bdn_db_name -f data/vm_hierarchie_taxo.sql  &>> logs/install_db.log


cd /home/$monuser/BDN
### Creation des listes de taxon spécifique à la structure
cp ./data/liste_taxons_structure.sql /tmp/liste_taxons_structure.sql
sudo sed -i -e "s/onfuser/$user_pg/g" /tmp/liste_taxons_structure.sql
echo "" &>> log/install_db.log
echo "" &>> log/install_db.log
echo "--------------------" &>> log/install_db.log
echo "Création des listes de taxons de la structure" &>> log/install_db.log
echo "--------------------" &>> log/install_db.log
export PGPASSWORD=$user_pg_pass;psql -h $pg_host -U $user_pg -d $bdn_db_name -f /tmp/liste_taxons_structure.sql  &>> log/install_db.log



######################################################################################################
######################################################################################################
###################################### INSTALATION DE la BASE BDN ####################################
######################################################################################################
######################################################################################################



echo "INSTALL DE LA BASE BDN" &>> log/install_db.log
echo "--------------------" &>> log/install_db.log
cp ./data/create_table_bdn.sql /tmp/create_table_bdn.sql
echo "--------------------" &>> log/install_db.log



echo "Creation des tables spatiales"
## creation des layers 

sudo -n -u postgres -s shp2pgsql -W "LATIN1" -s $projection -D -I ./data/layers/COMMUNE.shp layers.commune | sudo -n -u postgres -s psql -d $bdn_db_name

sudo -n -u postgres -s psql -d $bdn_db_name -c "ALTER TABLE layers.commune OWNER TO $user_pg;"
sudo -n -u postgres -s psql -d $bdn_db_name -c "ALTER TABLE layers.commune DROP CONSTRAINT commune_pkey; ALTER TABLE layers.commune ADD CONSTRAINT commune_pkey PRIMARY KEY (code_insee);"
 
sudo -n -u postgres -s shp2pgsql -W "LATIN1" -s $projection -D -I ./data/layers/perimetre_forets.shp layers.perimetre_forets | sudo -n -u postgres -s psql -d $bdn_db_name
sudo -n -u postgres -s psql -d $bdn_db_name -c "ALTER TABLE layers.perimetre_forets OWNER TO $user_pg;"
sudo -n -u postgres -s psql -d $bdn_db_name -c "ALTER TABLE layers.perimetre_forets DROP CONSTRAINT perimetre_forets_pkey; ALTER TABLE layers.perimetre_forets ADD CONSTRAINT perimetre_forets_pkey PRIMARY KEY (ccod_frt);"


sudo -n -u postgres -s shp2pgsql -W "LATIN1" -s $projection -D -I ./data/layers/mailles_1_2.shp layers.maille_1_2 | sudo -n -u postgres -s psql -d $bdn_db_name
sudo -n -u postgres -s psql -d $bdn_db_name -c "ALTER TABLE layers.maille_1_2 OWNER TO $user_pg;"
sudo -n -u postgres -s psql -d $bdn_db_name -c "ALTER TABLE layers.maille_1_2 DROP CONSTRAINT maille_1_2_pkey; ALTER TABLE layers.maille_1_2 ADD CONSTRAINT maille_1_2_pkey PRIMARY KEY (id_maille);
ALTER TABLE layers.maille_1_2 RENAME COLUMN taille_mai to taille_maille;"


sudo sed -i -e "s/onfuser/$user_pg/g" /tmp/create_table_bdn.sql
sudo sed -i -e "s/32620/$projection/g" /tmp/create_table_bdn.sql


echo "Creation de de la base ..."
sudo -n -u postgres -s psql -d $bdn_db_name -f /tmp/create_table_bdn.sql &>> log/install_db.log

#rm /tmp/create_table_bdn.sql



#Sauvegarde de la BDD
mkdir $backup_directory
mkdir $backup_directory/DAYLY
mkdir $backup_directory/MONTHLY



##### CONFIG APACHE FINALE ####
sudo a2enmod headers
sudo rm /etc/apache2/sites-available/000-default.conf
sudo rm /etc/apache2/sites-available/taxhub.conf
sudo a2dissite taxhub.conf

cp data/apache/apache.conf /tmp
sed -i -e "s/monuser/$monuser/g" /tmp/apache.conf
sed -i -e "s:mydomaine/$mondomaine:g" /tmp/apache.conf

sudo cp /tmp/apache.conf /etc/apache2/sites-available/000-default.conf


sudo apache2ctl restart