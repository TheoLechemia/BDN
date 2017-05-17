  #!/bin/bash

dos2unix settings.ini

. ./settings.ini


unzip ./data/taxref.zip

function database_exists () {
    # /!\ Will return false if psql can't list database. Edit your pg_hba.conf as appropriate.
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

rm  -f ./log/install_db.log
touch ./log/install_db.log


if database_exists $db_name
then
        if $drop_apps_db
            then
            echo "Suppression de la BDD..."
            sudo -n -u postgres -s dropdb $db_name  &>> log/install_db.log
        else
            echo "La base de données existe et le fichier de settings indique de ne pas la supprimer."
        fi
fi

# Sinon je créé la BDD
if ! database_exists $db_name 
then
  
echo "Création de la BDD..."

  sudo -u postgres psql -c "CREATE USER $user_bdn WITH PASSWORD '$user_bdn_pass'"
  sudo -n -u postgres -s createdb -O $user_bdn $db_name

  echo "Ajout de postGIS et pgSQL à la base de données"
  sudo -n -u postgres -s psql -d $db_name -c "CREATE EXTENSION IF NOT EXISTS postgis;"

  sudo -n -u postgres -s psql -d $db_name -c "CREATE SCHEMA contact_flore AUTHORIZATION $user_bdn;"
  sudo -n -u postgres -s psql -d $db_name -c "CREATE SCHEMA contact_faune AUTHORIZATION $user_bdn;"
  sudo -n -u postgres -s psql -d $db_name -c "CREATE SCHEMA synthese AUTHORIZATION $user_bdn;"
  sudo -n -u postgres -s psql -d $db_name -c "CREATE SCHEMA taxonomie AUTHORIZATION $user_bdn;"
  sudo -n -u postgres -s psql -d $db_name -c "CREATE SCHEMA layers AUTHORIZATION $user_bdn;"
  sudo -n -u postgres -s psql -d $db_name -c "CREATE SCHEMA fdw AUTHORIZATION $user_bdn;"
    sudo -n -u postgres -s psql -d $db_name -c "CREATE SCHEMA utilisateur AUTHORIZATION $user_bdn;"




#ajout de taxref

sudo -n -u postgres -s psql -d $db_name -c "CREATE EXTENSION file_fdw;"
sudo -n -u postgres -s psql -d $db_name -c "CREATE SERVER inpn FOREIGN DATA WRAPPER file_fdw;"
sudo -n -u postgres -s psql -d $db_name -c "CREATE FOREIGN TABLE fdw.taxref_v10 (regne character varying, phylum character varying, classe character varying,
ordre character varying, famille character varying, group1_inpn character varying,group2_inpn character varying,
cd_nom integer, cd_taxsup integer, cd_sup integer, cd_ref integer, rang character varying,
lb_nom character varying, lb_auteur character varying, nom_complet character varying, nom_complet_html character varying, nom_valide character varying,
nom_vern character varying, nom_vern_eng character varying, id_habitat integer, fr character varying,
gf character varying, mar character varying, gua character varying, sm character varying, sb character varying,
spm character varying, may character varying, epa character varying, reu character varying, sa character varying, ta character varying, taaf character varying,
pf character varying, nc character varying, wf character varying, cli character varying, url character varying) SERVER inpn
 OPTIONS (format 'csv', header 'true', filename '$taxref_path', delimiter E'\t', null '');"


 sudo -n -u postgres -s psql -d $db_name -c " GRANT SELECT ON fdw.taxref_v10 TO $user_bdn;"

echo "Création de la table Taxref ..."

 sudo -n -u postgres -s psql -d $db_name -c "CREATE TABLE taxonomie.taxref AS SELECT * FROM fdw.taxref_v10; 
  ALTER TABLE 
taxonomie.taxref ADD CONSTRAINT pk_taxref UNIQUE (cd_nom);"

sudo -n -u postgres -s psql -d $db_name -c "ALTER TABLE taxonomie.taxref OWNER TO $user_bdn;"

cp ./data/create_table_bdn.sql /tmp/create_table_bdn.sql

echo "Creation des tables spatiales"
## creation des layers 

 sudo -n -u postgres -s shp2pgsql -W "LATIN1" -s $projection -D -I ./data/layers/COMMUNE.shp layers.commune | sudo -n -u postgres -s psql -d $db_name

 sudo -n -u postgres -s psql -d $db_name -c " GRANT SELECT ON layers.commune TO $user_bdn;"
 sudo -n -u postgres -s psql -d $db_name -c "GRANT USAGE, SELECT ON SEQUENCE layers.commune_gid_seq TO $user_bdn;"
 


sudo -n -u postgres -s shp2pgsql -W "LATIN1" -s $projection -D -I ./data/layers/perimetre_forets.shp layers.perimetre_forets | sudo -n -u postgres -s psql -d $db_name
sudo -n -u postgres -s psql -d $db_name -c " GRANT SELECT ON layers.perimetre_forets TO $user_bdn;"
sudo -n -u postgres -s psql -d $db_name -c "GRANT USAGE, SELECT ON SEQUENCE layers.perimetre_forets_gid_seq TO $user_bdn;"

sudo -n -u postgres -s shp2pgsql -W "LATIN1" -s $projection -D -I ./data/layers/GLP_UTM20N1X1.shp layers.mailles_1k | sudo -n -u postgres -s psql -d $db_name
sudo -n -u postgres -s psql -d $db_name -c " GRANT SELECT ON layers.mailles_1k TO $user_bdn;"
sudo -n -u postgres -s psql -d $db_name -c "GRANT USAGE, SELECT ON SEQUENCE layers.mailles_1k_gid_seq TO $user_bdn;"

sudo -n -u postgres -s psql -d $db_name -c " ALTER TABLE layers.mailles_1k RENAME code_10km TO code_1km;"

sudo sed -i -e "s/onfuser/$user_bdn/g" /tmp/create_table_bdn.sql
sudo sed -i -e "s/32620/$projection/g" /tmp/create_table_bdn.sql
# sudo sed -i -e "s/listerougepath/$liste_rouge_path/g" /tmp/create_table_bdn.sql
# sudo sed -i -e "s/taxrefprotectionpath/$taxref_protection_path/g" /tmp/create_table_bdn.sql

echo "Creation de de la base ..."
sudo -n -u postgres -s psql -d $db_name -f /tmp/create_table_bdn.sql &>> log/install_db.log

rm /tmp/create_table_bdn.sql
rm ./TAXREFv10.0.txt
sudo -n -u postgres -s psql -d $db_name -c "DROP FOREIGN TABLE fdw.taxref_v10;"


#Sauvegarde de la BDD
mkdir $backup_directory
mkdir $backup_directory/DAYLY
mkdir $backup_directory/MONTHLY



fi