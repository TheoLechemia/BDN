# Documentation d'installation de BDN-DOM

### Infrastructure

L'application BDN-DOM peut être installée sur un serveur Linux (Ubuntu, Debian). Elle necessite au minimum 3Go de RAM et 20-25 Go d'espace disque.  
L'installation ci-dessous à été testée sur un serveur Ubuntu 16.04

### Téléchargement

Télécharger le projet depuis le dépôt Github:

`cd /home/monuser`  
`wget https://github.com/TheoLechemia/BDN/archive/X.Y.Z.zip `  

Dézipper l'archive  
`sudo apt-get install unzip`  
`unzip BDN-X.Y.Z.zip`  

Vous pouvez renommer le dossier qui contient l'application (dans un dossier /home/monuser/BDN/ par exemple)  

`mv BDN-X.Y.Z BDN`  

Placer vous ensuite dans le dossier qui contient l'application  

`cd BDN`  


### Préparation des données avant l'installation  
Avant de lancer le script d'installation il est nécessaire de préparer ses données pour l'application BDN. L'application a besoin de 4 fichiers personnalisés pour fonctionner:
- Une shapefile de ses communes
- Un shapefile des mailles de son territoire (1 ou 2km)
- Un shapefile du périmètre des forêts (facultatif pour les organisme non ONF)
- La liste rouge régionale de l'UICN (si elle existe)  

Par défaut, ce sont les fichiers paramétrés pour la Guadeloupe qui sont fournis. Remplacer par les fichiers existants par les vôtres dans le dossier `data/layers`  ou `data`  de l'application.  
:warning::warning: Veiller à bien garder les noms originaux des fichiers :warning::warning:  

#### Le shape des communes
Le shape doit à minima comporter les champs:
- 'NOM' pour le nom de la commune
- 'CODE_INSEE' pour le code insee.  

Nom du shape: COMMUNE.shp
#### Le shape des mailles
Ce shape de maille doit couvrir l'intégralité de votre territoire. L'application fonctionne avec des mailles de 1 et/ou 2 km
Il doit contenir les champs:
- TAILLE_MAI: la taille de ses mailles en KM
- ID_SERIAL : un serial...
- ID_MAILLE: l'identifiant unique de la maille  

Nom du shape: mailles_1_2.shp

#### Le shape du périmètre des forêts
Selon le modèle ONF du shape des périmètres forestiers. Celui-ci doit contenir à minima:  
- LIB_FRT: le nom de la forêt
- CCOD_FRT: le code de la forêt. :warning: Aucun enregistrement ne doit pas être NULL
Si vous ne disposez pas de couche de périmètre de forêt (hors ONF), laisser ce fichier par défaut  


Nom du shape: perimetre_forets.shp

#### La liste rouge régionale
Le fichier se trouve à la racine du dossier data: `Liste_rouge_regionale.csv`    
Voir http://uicn.fr/listes-rouges-regionales/ pour trouver celui de sa région

Une fois les fichiers remplacés, vous pouvez lancer l'installation
## Installation des applications et des bases de données

L'application BDN est fournie avec un script d'installation qui installe:
- UsersHub v1.2.2: une application pour la gestion centralisée des utilisateurs https://github.com/PnEcrins/UsersHub
- Taxhub v1.2.1: une application pour la gestion des taxons https://github.com/PnX-SI/TaxHub
- L'application BDN-DOM elle même  

En lançant ce script les dépendances suivantes sont installées:
* Python 2.7
* Flask
* Apache
* PostgreSQL / PostGIS
* PHP 5.6

Depuis la racine de l'application, lancer le script d'installation:  

`./install_app.sh`

Le fichier `settings.ini` s'ouvre: remplissez-le avec vos paramètres.
`Ctrl-O + Enter ` pour sauvegarder les modifications
`Ctrl-X + Enter ` pour continuer l'installation  
L'installation prend un certain temps... Cliquer sur 'ENTER' lorsque cela vous est demandé.  
Un second fichier de configuration apparait: celui de BDN: renseigner le champ `URL_APPLICATION` avec l'URL de votre serveur 
`Ctrl-O ` pour sauvegarder les modifications
`Ctrl-X ` pour continuer l'installation  
Deux autres fichiers de configuration de taxhub apparaissent ensuite. Modifiez les en fonction de vos paramètres.  

:clap: DONE !! :clap:

Les applications sont disponibles aux addresses suivantes:
- BDN: http://url_serveur/
- UsersHub: http://url_serveur/usershub
- Taxhub: http://url_serveur/usershub

Un compte administrateur est créé par défaut: ID: admin MDP: admin

Les logs de l'instalation sont disponibles dans le dossier log pour vérifier d'éventuelles erreurs.




## Sauvegarde automatique
Pour effectuer des sauvegardes automatiques des bases de données (BDN et UsersHub + l'atlas s'il est installé)  
Dans un terminalde commande, tapez:  
`crontab -e`  
et ajouter la ligne suivante à la fin du fichier:  
` 45 23 * * * /home/<USER>/BDN/cron_pg_backup.sh`  
Cette commande va ainsi faire des sauvegardes journalières et mensuelles de la BDD


