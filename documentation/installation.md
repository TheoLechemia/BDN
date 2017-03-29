# Instalation de BDN-DOM

Cloner le dépôt  
`git clone https://github.com/TheoLechemia/BDN.git `  
`cd ./BDN`

### Instalation de l'environnement et de l'application
* Python 2.7
* Flask
* Apache
* PostgreSQL / PostGIS

`./install_app.sh`  

### Installation de la base de données
`./install_db.sh`  

### Configuration Apache
`sudo nano /etc/apache2/sites-available/BDN.conf`  
Copiez collez   
```WSGIScriptAlias / /home/MONUSER/atlas/start.wsgi  
 <Directory "/home/MONUSER/bdn">  
   WSGIApplicationGroup %{GLOBAL}  
   WSGIScriptReloading On  
   Require all granted  
 </Directory>
 ```  
 
Activez le virtualhost puis redémarrez Apache :  

`sudo a2ensite bdn`
`sudo apachectl restart`  

## Configuration de l'application

Ouvrir et éditer les fichiers
`/home/MON_USER/BDN/config.py.sample` et `/home/MON_USER/BDN/settings.ini.sample`  
Mettre le fichier de liste rouge de l'UICN correspondant à sa région dans `./data` s'il en existe un, et renseigner le chemin correct vers ce fichier dans `settings.ini`

`sudo apachectl restart`


## Sauvegarde automatique
Taper `crontab -e`  
et ajouter la ligne suivante à la fin du fichier:  
` 45 23 * * * /home/ubuntu/BDN/cron_pg_backup.sh`  
Cette commande va ainsi faire des sauvegarde journalière et mensuelles de la BDD


