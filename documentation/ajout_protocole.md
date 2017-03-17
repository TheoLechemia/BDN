# Ajouter un protocole personnalisé

L'application permet d'ajouter facilement un protocole personnalisé à partir d'un fichier tableur grâce à la commande `create_protocole.py`  

Le module générique **addObs** permet d'ajouter en base de données des observations de type contact de différents protocoles reprennant les champs:   
"QUI: l'observateur  
"QUOI": le taxon  
"OU": la localisation de l'observation  
"Quand": la date de l'observation  
"COMMENT" : les champs propres à chaque protocole

La commande `create_protocole` permet de creer une nouvelle table en base de données, ainsi qu'un template HTML pour renseigner des observations de son protocole dans le module **addObs**.  
Pour cela, remplissez le fichier `/home/USER/BDN/modele_protocole.xls`  
  
![modele_protocole](https://github.com/TheoLechemia/BDN/blob/master/documentation/images/modele_protocoe.PNG)
  
  
**Colonne Nom Champs**:  
Renseignez le nom du champ tel qu'il sera entré en BDD (pas d'espace, ni de caractère spéciaux)  
  
**Colonne Type**:
Renseignez ici le type du champ pour l'affichage HTML du formulaire (entier, liste déroulante, booléen)
  
**Colonne Type en base de données**:
Renseignez le type SQL (integer, character varying, float etc...)
  
**Colonnes Choix**:
Si il s'agit d'un champs à choix multiple, renseignez l'ensemble des choix  

Enregistrez le fichier en .CSV . Le nom du protocole en BDD sera le nom de ce fichier.  
Ouvrez ensuite le fichier à l'aide du bloc note pour changer l'encoding
![modele_protocole](https://github.com/TheoLechemia/BDN/blob/master/documentation/images/utf_8.png)

Lancez la commande `python create_protocole.py`  
La commande demande le chemin entier vers le fichier, renseignez le...

Done !



## Que fais cette commande ?

* Creation d'un nouveau schema en BDD au nom du fichier CSV
* Création d'une table `nom_protocole.releve` qui comportera l'ensemble des observations
* Création d'une "bib" comportant tous les champs spécifiques au protocole ainsi que le contentu des listes déroulantes
* Création d'une vue `taxonomie.taxons_nom_protocole` dans le schéma taxonomie

Par défault, la vue `taxonomie.taxons_nom_protocole` embarque tout le taxref. Personnalisez cette vue pour y afficher seulement les taxons corespondant à votre protocole. Seul ces taxons seront proposés alors dans le formulaire de saisie.






