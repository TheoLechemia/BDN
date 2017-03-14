CREATE TABLE synthese.syntheseff
(
  id_synthese serial,
  protocole character varying(50) NOT NULL,
  observateur character varying(100) NOT NULL,
  date date NOT NULL,
  cd_nom integer NOT NULL,
  insee character varying(10),
  altitude integer,
  valide boolean,
  geom_point geometry(Point,32620),
  ccod_frt character varying(50),
  code_maille character varying(20),
  loc_exact boolean,
  id_structure integer,
  CONSTRAINT synthese_pkey PRIMARY KEY (id_synthese),
  CONSTRAINT cd_nom FOREIGN KEY (cd_nom)
      REFERENCES taxonomie.taxref (cd_nom) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE SET NULL
);
ALTER TABLE synthese.syntheseff
  OWNER TO onfuser;


CREATE TABLE contact_faune.freleve
(
  id_obs serial NOT NULL,
  id_synthese character varying(15),
  observateur character varying(100) NOT NULL,
  date date NOT NULL,
  cd_nom integer NOT NULL,
  geom_point geometry(Point,32620),
  insee character varying(10),
  altitude integer,
  commentaire character varying(150),
  valide boolean,
  ccod_frt character varying(50),
  loc_exact boolean,
  code_maille character varying(20),
  id_structure integer,
  type_obs character varying(50),
  nb_individu_approx character varying(50),
  comportement character varying(50),
  nb_non_identife integer,
  nb_male integer,
  nb_femelle integer,
  nb_jeune integer,
  trace character varying(50),
  

  CONSTRAINT faune_pkey PRIMARY KEY (id_obs),
  CONSTRAINT cd_nom FOREIGN KEY (cd_nom)
      REFERENCES taxonomie.taxref (cd_nom) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT fa_id_synthese UNIQUE (id_synthese)
);


ALTER TABLE contact_faune.releve
  OWNER TO onfuser;

CREATE TABLE contact_flore.releve
(
  id_obs serial NOT NULL,
  id_synthese character varying(15),
  observateur character varying(100) NOT NULL,
  date date NOT NULL,
  cd_nom integer NOT NULL,
  geom_point geometry(Point,32620),
  insee character varying(10),
  altitude integer,
  commentaire character varying(150),
  valide boolean,
  ccod_frt character varying(50),
  loc_exact boolean,
  code_maille character varying(20),
  id_structure integer,
  abondance character varying(15),
  nb_pied_approx character varying(15),
  nb_pied integer,
  stade_dev character varying(50),
  
  CONSTRAINT fl_pk PRIMARY KEY (id_obs),
  CONSTRAINT cd_nom FOREIGN KEY (cd_nom)
      REFERENCES taxonomie.taxref (cd_nom) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT fl_id_synthese UNIQUE (id_synthese)
);
  ALTER TABLE contact_flore.releve
    OWNER TO onfuser;


  -- Trigger
-- create id_synthese in protocole

CREATE OR REPLACE FUNCTION synthese.tr_protocole_to_synthese() RETURNS TRIGGER AS $tr_protocole_to_synthese$
    DECLARE newid INTEGER;
    DECLARE schemaname character varying;
    BEGIN
    schemaname = quote_ident(tg_table_schema);
    INSERT INTO synthese.syntheseff (protocole, observateur, date, cd_nom, insee, ccod_frt, altitude, valide,geom_point, loc_exact, code_maille, id_structure) 
    VALUES( tg_table_schema, new.observateur, new.date, new.cd_nom, new.insee, new.ccod_frt, new.altitude, new.valide, new.geom_point, new.loc_exact, new.code_maille, new.id_structure) ;
    SELECT INTO newid currval('synthese.syntheseff_id_synthese_seq');
    EXECUTE format('
    UPDATE %s.%s SET id_synthese = %s;', TG_TABLE_SCHEMA, TG_TABLE_NAME, newid);
    RETURN NEW;
  
    END;
$tr_protocole_to_synthese$ LANGUAGE plpgsql;

CREATE TRIGGER tr_fa_to_synthese
AFTER INSERT ON contact_faune.releve
    FOR EACH ROW EXECUTE PROCEDURE synthese.tr_protocole_to_synthese();

CREATE TRIGGER tr_fl_to_synthese
AFTER INSERT ON contact_flore.releve
    FOR EACH ROW EXECUTE PROCEDURE synthese.tr_protocole_to_synthese();


-- end trigger

CREATE OR REPLACE VIEW synthese.v_search_taxons AS 
 SELECT DISTINCT s.cd_nom,
    t.nom_vern,
    t.lb_nom,
    s.protocole
   FROM synthese.syntheseff s
     JOIN taxonomie.taxref t ON s.cd_nom = t.cd_nom;

ALTER TABLE synthese.v_search_taxons
  OWNER TO onfuser;


CREATE TABLE synthese.bib_protocole (
nom_protocole character varying CONSTRAINT bib_protocole_pk PRIMARY KEY,
nom_schema character varying,
nom_table character varying,
nom_complet character varying,
template character varying,
bib_champs character varying
);
ALTER TABLE synthese.bib_protocole
    OWNER TO onfuser;


INSERT INTO synthese.bib_protocole VALUES ('Contact Flore', 'contact_flore', 'releve', 'contact_flore.releve', 'addObs/contactFlore.html', 'contact_flore.bib_champs_contact_flore'), ('Contact Faune','contact_faune', 'releve', 'contact_faune.releve', 'addObs/contactFaune.html', 'contact_faune.bib_champs_contact_faune');

CREATE TABLE contact_faune.bib_champs_contact_faune(
id serial  CONSTRAINT bib_fa_primary_key PRIMARY KEY,
nom_champ character varying,
valeur character varying
);
ALTER TABLE contact_faune.bib_champs_contact_faune
    OWNER TO onfuser;



INSERT INTO contact_faune.bib_champs_contact_faune (nom_champ, valeur) VALUES
('type_obs', 'Contact visuel'),
('type_obs', 'Chant'),
('type_obs', 'Cris'),
('type_obs', 'Nid'),
('type_obs', 'Gîte'),
('type_obs', 'Nichoir'),
('type_obs', 'Empreintes, traces'),
('type_obs', 'Détection'),
('type_obs', 'Capture manuelle'),
('type_obs', 'Indices (crottes,...)'),
('type_obs', 'Animal mort ou collision'),
('effectif', '1-5'),
('effectif', '6-10'),
('effectif', '11-20'),
('effectif', '21-50'),
('effectif', '51-100'),
('effectif', '101-500'),
('effectif', '501-1000'),
('effectif', '>1000'),
('comportement', 'Reproduction'),
('comportement', 'Parade nuptiale'),
('comportement', 'Ponte'),
('comportement', 'Nidification'),
('comportement', 'Emergence'),
('comportement', 'Eclosion'),
('comportement', 'Comportement parental'),
('comportement', 'Colonie avec mise bas'),
('comportement', 'Colonie de reproduction'),
('comportement', 'Colonie avec certaines femelles gestantes'),
('comportement', 'Colonie avec jeunes non volants'),
('comportement', 'Colonie avec jeunes volants'),
('comportement', 'Colonie sans jeunes'),
('comportement', 'Colonie avec males'),
('comportement', 'Individus isolés'),
('comportement', 'En chasse'),
('comportement', 'En vol'),
('comportement', 'Fuite'),
('comportement', 'Alerte'),
('comportement', 'Repos'),
('comportement', 'Léthargie diurne'),
('comportement', 'Alimentation'),
('comportement', 'Transit'),
('comportement', 'Estivage'),
('comportement', 'Migration'),
('comportement', 'Harem'),
('comportement', 'Autres'),
('trace', 'Crottes ou crottier'),
('trace', 'Ecorçage ou frottis'),
('trace', 'Empreintes'),
('trace', 'Epiderme'),
('trace', 'Guano'),
('trace', 'Nid'),
('trace', 'Oeufs'),
('trace', 'Pelage'),
('trace', 'Pelotes de réjection'),
('trace', 'Restes alimentaires'),
('trace', 'Restes de l"animal'),
('trace', 'Terrier'),
('trace', 'Larves'),
('trace', 'Exuvie');




CREATE TABLE contact_flore.bib_champs_contact_flore(
id serial  CONSTRAINT bib_fl_primary_key PRIMARY KEY,
nom_champ character varying,
valeur character varying
);
ALTER TABLE contact_flore.bib_champs_contact_flore
    OWNER TO onfuser;

INSERT INTO contact_flore.bib_champs_contact_flore (nom_champ, valeur) VALUES
('abondance', '1'),
('abondance', '2-3'),
('abondance', '4-5'),
('abondance', '6-50'),
('abondance', '< 5%'),
('abondance', '5-25%'),
('abondance', '16-25%'),
('abondance', '26-50%'),
('abondance', '51-75%'),
('abondance', '76-100%'),
('nb_pied_approx', '1 à 10'),
('nb_pied_approx', '10 à 100'),
('nb_pied_approx', 'Plus de 100'),
('nb_pied_approx', 'Plus de 100'),
('stade_dev', 'Stade végétatif'),
('stade_dev', 'Stade bouton floraux'),
('stade_dev', 'Début floraison'),
('stade_dev', 'Pleine floraison'),
('stade_dev', 'Fin de floraison et maturation des fruits'),
('stade_dev', 'Dissémination'),
('stade_dev', 'Stade de décrépitude');




-- Taxonomie

--habitat du taxref
CREATE TABLE taxonomie.bib_habitat (
id integer,
type character varying
);

ALTER TABLE taxonomie.bib_habitat
  OWNER TO onfuser;

CREATE OR REPLACE FUNCTION taxonomie.find_cdref(id integer)
  RETURNS integer AS
$BODY$
--fonction permettant de renvoyer le cd_ref d'un taxon à partir de son cd_nom
--
--Gil DELUERMOZ septembre 2011

  DECLARE ref integer;
  BEGIN
  SELECT INTO ref cd_ref FROM taxonomie.taxref WHERE cd_nom = id;
  return ref;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE;

INSERT INTO taxonomie.bib_habitat 
VALUES (1, 'Marin'), (2, 'Eau douce'), (3, 'Terrestre'), (4,'Marin et eau douce' ), (5, 'Marin et Terrestre' ), (6,'Eau saumâtre'), (7, 'Continental (terrestre et/ou eau douce)'), (8,'Continental (terrestre et eau douce)' );

--liste rouge
CREATE TABLE taxonomie.liste_rouge(
ordre integer,
cd_ref integer,
cd_nom integer ,
nom_cite character varying,
auteur character varying,
nom_communs character varying,
population character varying,
rang character varying,
famille character varying,
endemisme character varying,
commentaire character varying,
statut character varying,
criteres character varying,
tendance character varying,
version integer,
statut_i character varying,
statut_eu character varying,
anneeval character varying,
nom_liste character varying,
type_liste character varying,
groupe_grand_public character varying
);

ALTER TABLE taxonomie.liste_rouge
  OWNER TO onfuser;

COPY taxonomie.liste_rouge
FROM E'/home/ubuntu/BDN/data/Liste_rouge_Guadeloupe.txt'
WITH (format 'csv', header 'true', delimiter E';');

--espece protege taxref
CREATE TABLE taxonomie.protection (
cd_nom integer,
cd_protection character varying,
nom_cite character varying,
syn_cite character varying,
nom_francais_cite character varying,
precisions character varying,
cd_nom_cite integer
);

ALTER TABLE taxonomie.protection
  OWNER TO onfuser;



COPY taxonomie.protection
FROM E'/home/ubuntu/BDN/data/PROTECTION_ESPECES_10.txt'
WITH (format 'csv', header 'true', delimiter E';');



-- Creation des vues de la liste des taxons personnalisée pour la structure: ICI la liste des taxons antillais / faune et flore
CREATE VIEW taxonomie.taxons_contact_flore AS(
SELECT taxonomie.find_cdref(cd_nom) AS cd_ref, nom_vern, lb_nom
FROM taxonomie.taxref
WHERE (mar != 'A' OR gua != 'A' OR sm != 'A' OR sb != 'A') AND regne = 'Plantae'
);

ALTER TABLE taxonomie.taxons_contact_flore
  OWNER TO onfuser;

CREATE VIEW taxonomie.taxons_contact_faune AS(
SELECT taxonomie.find_cdref(cd_nom) AS cd_ref, nom_vern, lb_nom
FROM taxonomie.taxref
WHERE (mar != 'A' OR gua != 'A' OR sm != 'A' OR sb != 'A') AND regne = 'Animalia'
);

ALTER TABLE taxonomie.taxons_contact_faune
  OWNER TO onfuser;

CREATE TABLE taxonomie.bib_liste_rouge (
id_statut character varying,
type_statut character varying
);

INSERT INTO taxonomie.bib_liste_rouge 
VALUES('NE', 'Non évalué'),
('NA', 'Non applicable'),
('DD', 'Données insuffisante'),
('LC', 'Préoccupation mineure'),
('QT', 'Quasi menacée'),
('VU', 'Vulnérable'),
('EN', 'En danger'),
('CR', 'En danger critique'),
('RE', 'Disparu au niveau régional'),
('EW', 'Eteinte à l''état sauvage'),
('EX', 'Eteinte') ;

ALTER TABLE taxonomie.bib_liste_rouge
  OWNER TO onfuser;



  -- Creation des vues pour les exports en shapefile

CREATE OR REPLACE VIEW bdn.faune_poly AS 
 SELECT t.nom_vern,
    t.lb_nom,
    f.id_obs,
    f.id_synthese,
    f.protocole,
    f.observateur,
    f.date,
    f.cd_nom,
    f.insee,
    f.altitude,
    f.type_obs,
    f.nb_individu_approx,
    f.comportement,
    f.nb_non_identife,
    f.nb_male,
    f.nb_femelle,
    f.nb_jeune,
    f.trace,
    f.commentaire,
    f.ccod_frt,
    m.code_1km,
    m.geom

   FROM bdn.faune f
     JOIN layers.mailles_1k m ON m.code_1km::text = f.code_maille::text AND f.valide=true
     JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom;


CREATE OR REPLACE VIEW contact_faune.faune_point AS 
 SELECT
    t.nom_vern,
    t.lb_nom,
    f.id_obs,
    f.id_synthese,
    f.protocole,
    f.observateur,
    f.date,
    f.cd_nom,
    f.insee,
    f.altitude,
    f.type_obs,
    f.nb_individu_approx,
    f.comportement,
    f.nb_non_identife,
    f.nb_male,
    f.nb_femelle,
    f.nb_jeune,
    f.trace,
    f.geom_point,
    f.commentaire,
    f.ccod_frt

   FROM contact_faune.releve f
   JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
  WHERE f.loc_exact = true;

  CREATE OR REPLACE VIEW contact_flore.flore_point AS 
 SELECT 
    t.nom_vern,
    t.lb_nom,
    flore.id_obs,
    flore.id_synthese,
    flore.protocole,
    flore.observateur,
    flore.date,
    flore.cd_nom,
    flore.insee,
    flore.altitude,
    flore.abondance,
    flore.nb_pied_approx,
    flore.nb_pied,
    flore.stade_dev,
    flore.geom_point,
    flore.commentaire,
    flore.ccod_frt

   FROM contact_flore.releve flore
   JOIN taxonomie.taxref t ON t.cd_nom = flore.cd_nom
  WHERE flore.loc_exact = true AND flore.valide = true;

  CREATE OR REPLACE VIEW contact_flore.flore_poly AS 
 SELECT 
    t.nom_vern,
    t.lb_nom,
    f.id_obs,
    f.id_synthese,
    f.protocole,
    f.observateur,
    f.date,
    f.cd_nom,
    f.insee,
    f.altitude,
    f.abondance,
    f.nb_pied_approx,
    f.nb_pied,
    f.stade_dev,
    f.commentaire,
    f.ccod_frt,
    f.code_maille,
    m.code_1km,
    m.geom

   FROM contact_flore.flore f
     JOIN layers.mailles_1k m ON m.code_1km::text = f.code_maille::text AND f.valide = true
     JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom;


-- schema utilisateur


CREATE TABLE utilisateur.login
(
  id serial NOT NULL,
  nom character varying,
  mpd character varying,
  auth_role integer,
  id_structure integer,
  CONSTRAINT primary_key PRIMARY KEY (id)
);

ALTER TABLE utilisateur.login
  OWNER TO onfuser;

INSERT INTO utilisateur.login
VALUES(1, 'admin', 'admin', 3, 1 );



CREATE TABLE utilisateur.bib_structure(
id_structure integer,
nom_structure character varying
);

ALTER TABLE utilisateur.bib_structure
  OWNER TO onfuser;

INSERT INTO utilisateur.bib_structure
VALUES(1, 'ONF'), (2, 'Réserves');

CREATE TABLE utilisateur.bib_role(
auth_role integer,
descritption character varying
);

ALTER TABLE utilisateur.bib_role
  OWNER TO onfuser;


INSERT INTO utilisateur.bib_role
VALUES(1, 'lecteur'), (2, 'contributeur'), (3, 'administrateur');


