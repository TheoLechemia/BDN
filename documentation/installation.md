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
Copier le fichier setting.ini.sample en settings.ini et le remplir en suivant les instructions  
`cp ./settings.ini.sample ./settings.ini`  
`nano ./settings.ini`  
Mettre le fichier de liste rouge de l'UICN correspondant à sa région dans `./data` s'il en existe un, et renseigner le chemin correct vers ce fichier dans `settings.ini`  
Lancer le script de création de la BDD  
`./install_db.sh` 


### Configuration Apache
`sudo nano /etc/apache2/sites-available/BDN.conf`  
Copiez collez   
```WSGIScriptAlias / /home/<USER>/atlas/start.wsgi  
 <Directory "/home/<USER>/bdn">  
   WSGIApplicationGroup %{GLOBAL}  
   WSGIScriptReloading On  
   Require all granted  
 </Directory>
 ```  
 
Activez le virtualhost puis redémarrez Apache :  

`sudo a2ensite bdn`
`sudo apachectl restart`  

## Configuration de l'application

Ouvrir et éditer le fichiers
`/home/<USER>/BDN/config.py.sample`

`sudo apachectl restart`


## Sauvegarde automatique
Taper `crontab -e`  
et ajouter la ligne suivante à la fin du fichier:  
` 45 23 * * * /home/<USER>/BDN/cron_pg_backup.sh`  
Cette commande va ainsi faire des sauvegarde journalière et mensuelles de la BDD


