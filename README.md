# BDN-DOM
### Application web de gestion des données naturalistes développée par l'ONF Guadeloupe

L'application BDN-DOM contient plusieurs sous-modules qui peuvent être utilisées indépendemment:
* Un module générique de saisie  des données de différents protocoles
* Un module d'import de fichiers CSV dans une base PostregreSQL
* un module de validation des données
* un module de synthèse pour la visualisation et le téléchargement des données en shapefiles
* un module de téléchargement des données pour télécharger le modele de données exact de chaque projet
* un module de gestion des projets (création de nouveau projet/protocole, edition des métadonnées)

L'application s'appuie sur des application connexes développées par les parc nationaux français:
- UsersHub v1.2.2: une application pour la gestion centralisée des utilisateur https://github.com/PnEcrins/UsersHub
- Taxhub v1.2.1: une application pour la gestion des taxons https://github.com/PnX-SI/TaxHub

L'application BDN-DOM est un projet open-source: elle peut être deployée dans d'autres structures que l'ONF:  
:arrow_forward: [Installer l'application](https://github.com/TheoLechemia/BDN/blob/master/documentation/installation.md)

### Technologies:
* Base de données: PostgreSQL - PostGIS
* Back-end: Python Flask
* Front-End : Angular 1.5, Leaflet

### Documentation
##### [Installer l'application](https://github.com/TheoLechemia/BDN/blob/master/documentation/installation.md)

### Aperçu
#### Le tableau de bord:  
![modele_protocole](https://github.com/TheoLechemia/BDN/blob/master/documentation/images/accueil.PNG)  

#### Le module de synthèse:
![modele_protocole](https://github.com/TheoLechemia/BDN/blob/master/documentation/images/synthese.PNG)

#### Le module de saisie des observations:  
![modele_protocole](https://github.com/TheoLechemia/BDN/blob/master/documentation/images/addObs_bis.PNG)










