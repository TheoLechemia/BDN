-- PEUPLEMEMENT DE LA TABLE BIB_NOM
INSERT INTO taxonomie.bib_noms (cd_nom,cd_ref,nom_francais)
SELECT cd_nom, cd_ref, nom_vern FROM taxonomie.import_taxref 
WHERE mar != 'A' OR gua != 'A' OR sm != 'A' OR sb != 'A';


-- CREATION DES LISTE contact_faune / contact_flore dans taxhub

INSERT INTO taxonomie.bib_listes VALUES
 (1005, 'contact_faune', 'Liste servant à la saisi du projet contact faune', 'images/pictos/nopicto.gif', 'Animalia', '' )
,(1006, 'contact_flore', 'Liste servant à la saisi du projet contact flore', 'images/pictos/nopicto.gif', 'Plantae', '' );

INSERT INTO taxonomie.cor_nom_liste (id_liste,id_nom)
SELECT 1005,n.id_nom FROM taxonomie.bib_noms n
JOIN taxonomie.import_taxref t ON t.cd_nom = n.cd_nom
where  (mar != 'A' OR gua != 'A' OR sm != 'A' OR sb != 'A') AND t.regne = 'Animalia';

INSERT INTO taxonomie.cor_nom_liste (id_liste,id_nom)
SELECT 1006,n.id_nom FROM taxonomie.bib_noms n
JOIN taxonomie.import_taxref t ON t.cd_nom = n.cd_nom
where  (mar != 'A' OR gua != 'A' OR sm != 'A' OR sb != 'A') AND t.regne = 'Plantae';

-- Peuplement des LISTES


-- Creation des vues de la liste des taxons personnalisée pour la structure: ICI la liste des taxons antillais / faune et flore


CREATE MATERIALIZED VIEW taxonomie.taxons_contact_faune AS (

SELECT taxonomie.find_cdref(t3.cd_nom) AS cd_ref, t3.cd_nom, nom_valide, lb_nom, CONCAT(t3.lb_nom, ' = ', t3.nom_complet_html) AS search_name
from taxonomie.cor_nom_liste t1
JOIN taxonomie.bib_noms t2 ON t1.id_nom = t2.id_nom
JOIN taxonomie.taxref t3 ON t3.cd_nom = t2.cd_nom
WHERE t1.id_liste = 1005
UNION
SELECT taxonomie.find_cdref(t3.cd_nom),t3.cd_nom, nom_valide,  lb_nom, CONCAT(t3.nom_vern, ' = ', t3.nom_complet_html) AS search_name
from taxonomie.cor_nom_liste t1
JOIN taxonomie.bib_noms t2 ON t1.id_nom = t2.id_nom
JOIN taxonomie.taxref t3 ON t3.cd_nom = t2.cd_nom
WHERE t1.id_liste = 1005 AND t3.nom_vern IS NOT NULL
);

ALTER TABLE taxonomie.taxons_contact_faune
  OWNER TO onfuser;


CREATE MATERIALIZED VIEW taxonomie.taxons_contact_flore AS (

SELECT taxonomie.find_cdref(t3.cd_nom) AS cd_ref, t3.cd_nom, nom_valide, lb_nom, CONCAT(t3.lb_nom, ' = ', t3.nom_complet_html) AS search_name
from taxonomie.cor_nom_liste t1
JOIN taxonomie.bib_noms t2 ON t1.id_nom = t2.id_nom
JOIN taxonomie.taxref t3 ON t3.cd_nom = t2.cd_nom
WHERE t1.id_liste = 1006

UNION
SELECT taxonomie.find_cdref(t3.cd_nom), t3.cd_nom, nom_valide,lb_nom, CONCAT(t3.nom_vern, ' = ', t3.nom_complet_html) AS search_name
from taxonomie.cor_nom_liste t1
JOIN taxonomie.bib_noms t2 ON t1.id_nom = t2.id_nom
JOIN taxonomie.taxref t3 ON t3.cd_nom = t2.cd_nom
WHERE t1.id_liste = 1006 AND t3.nom_vern IS NOT NULL
);

ALTER TABLE taxonomie.taxons_contact_flore
  OWNER TO onfuser;