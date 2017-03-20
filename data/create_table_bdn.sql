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
  geom_poly geometry(Geometry,32620),
  loc_exact boolean,
  id_structure integer,
  CONSTRAINT synthese_pkey PRIMARY KEY (id_synthese),
  CONSTRAINT cd_nom FOREIGN KEY (cd_nom)
      REFERENCES taxonomie.taxref (cd_nom) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE SET NULL
);
ALTER TABLE synthese.syntheseff
  OWNER TO onfuser;


CREATE TABLE contact_faune.releve
(
  id_obs serial NOT NULL,
  id_synthese integer,
  observateur character varying(100) NOT NULL,
  date date NOT NULL,
  cd_nom integer NOT NULL,
  geom_point geometry(Point,32620),
  insee character varying(10),
  altitude integer,
  commentaire character varying(150),
  comm_loc character varying(150),
  valide boolean,
  ccod_frt character varying(50),
  loc_exact boolean,
  geom_poly geometry(Polygon,32620),
  id_structure integer,
  type_obs character varying(50),
  effectif character varying(50),
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
  id_synthese integer,
  observateur character varying(100) NOT NULL,
  date date NOT NULL,
  cd_nom integer NOT NULL,
  geom_point geometry(Point,32620),
  insee character varying(10),
  altitude integer,
  commentaire character varying(150),
  comm_loc character varying(150),
  valide boolean,
  ccod_frt character varying(50),
  loc_exact boolean,
  geom_poly geometry(Polygon,32620),
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
    DECLARE protocoleid INTEGER;
    BEGIN
 
    INSERT INTO synthese.syntheseff (protocole, observateur, date, cd_nom, insee, ccod_frt, altitude, valide,geom_point, loc_exact, geom_poly, id_structure) 
    VALUES(tg_table_schema, new.observateur, new.date, new.cd_nom, new.insee, new.ccod_frt, new.altitude, new.valide, new.geom_point, new.loc_exact, new.geom_poly, new.id_structure) RETURNING new.id_obs INTO protocoleid;
    SELECT INTO newid currval('synthese.syntheseff_id_synthese_seq');
    EXECUTE format('
    UPDATE %s.%s SET id_synthese = %s WHERE id_obs=%s;', TG_TABLE_SCHEMA, TG_TABLE_NAME, newid, protocoleid);
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
id_champ integer,
no_spec character varying,
nom_champ character varying,
valeur character varying
);
ALTER TABLE contact_faune.bib_champs_contact_faune
    OWNER TO onfuser;



INSERT INTO contact_faune.bib_champs_contact_faune (id_champ, nom_champ, valeur, no_spec) VALUES
(1,'type_obs', 'Contact visuel', 'spec_1'),
(2,'type_obs', 'Chant', 'spec_1'),
(3,'type_obs', 'Cris', 'spec_1'),
(4, 'type_obs', 'Contact sonore', 'spec_1'),
(5,'type_obs', 'Nid', 'spec_1'),
(6,'type_obs', 'Gîte', 'spec_1'),
(7,'type_obs', 'Nichoir', 'spec_1'),
(8,'type_obs', 'Empreintes, traces', 'spec_1'),
(9,'type_obs', 'Détection', 'spec_1'),
(10,'type_obs', 'Indices (crottes,...)', 'spec_1'),
(11,'type_obs', 'Animal mort ou collision', 'spec_1'),
(1,'effectif', '1-5','spec_2'),
(2,'effectif', '6-10','spec_2'),
(3,'effectif', '11-20','spec_2'),
(4,'effectif', '21-50','spec_2'),
(5,'effectif', '51-100','spec_2'),
(6,'effectif', '101-500','spec_2'),
(7,'effectif', '501-1000','spec_2'),
(8,'effectif', '>1000','spec_2'),
(1,'comportement', 'Reproduction','spec_3'),
(2,'comportement', 'Parade nuptiale','spec_3'),
(3,'comportement', 'Ponte','spec_3'),
(4,'comportement', 'Nidification','spec_3'),
(5,'comportement', 'Emergence','spec_3'),
(6,'comportement', 'Eclosion','spec_3'),
(7,'comportement', 'Comportement parental','spec_3'),
(8,'comportement', 'Colonie avec mise bas','spec_3'),
(9,'comportement', 'Colonie de reproduction','spec_3'),
(10,'comportement', 'Colonie avec certaines femelles gestantes','spec_3'),
(11,'comportement', 'Colonie avec jeunes non volants','spec_3'),
(12,'comportement', 'Colonie avec jeunes volants','spec_3'),
(13,'comportement', 'Colonie sans jeunes','spec_3'),
(14,'comportement', 'Colonie avec males','spec_3'),
(15,'comportement', 'Individus isolés','spec_3'),
(16,'comportement', 'En chasse','spec_3'),
(17,'comportement', 'En vol','spec_3'),
(18,'comportement', 'Fuite','spec_3'),
(19,'comportement', 'Alerte','spec_3'),
(20,'comportement', 'Repos','spec_3'),
(21,'comportement', 'Léthargie diurne','spec_3'),
(22,'comportement', 'Alimentation','spec_3'),
(23,'comportement', 'Transit','spec_3'),
(24,'comportement', 'Estivage','spec_3'),
(25,'comportement', 'Migration','spec_3'),
(26,'comportement', 'Harem','spec_3'),
(27,'comportement', 'Autres','spec_3'),
(NULL, 'nb_male', '', 'spec_4'),
(NULL, 'nb_femelle', '', 'spec_5'),
(NULL, 'nb_jeune', '', 'spec_6'),
(NULL, 'nb_non_identife', '', 'spec_7'),
(1,'trace', 'Crottes ou crottier','spec_8'),
(2,'trace', 'Ecorçage ou frottis','spec_8'),
(3,'trace', 'Empreintes','spec_8'),
(4,'trace', 'Epiderme','spec_8'),
(5,'trace', 'Guano','spec_8'),
(6,'trace', 'Nid','spec_8'),
(7,'trace', 'Oeufs','spec_8'),
(8,'trace', 'Pelage','spec_8'),
(9,'trace', 'Pelotes de réjection','spec_8'),
(10,'trace', 'Restes alimentaires','spec_8'),
(11,'trace', 'Restes de l"animal','spec_8'),
(12,'trace', 'Terrier','spec_8'),
(13,'trace', 'Larves','spec_8'),
(14,'trace', 'Exuvie','spec_8');




CREATE TABLE contact_flore.bib_champs_contact_flore(
id serial  CONSTRAINT bib_fl_primary_key PRIMARY KEY,
id_champ integer,
no_spec character varying,
nom_champ character varying,
valeur character varying
);
ALTER TABLE contact_flore.bib_champs_contact_flore
    OWNER TO onfuser;

INSERT INTO contact_flore.bib_champs_contact_flore (id_champ, nom_champ, valeur, no_spec) VALUES
(1,'abondance', '1','spec_1'),
(2,'abondance', '2-3','spec_1'),
(3,'abondance', '4-5','spec_1'),
(4,'abondance', '6-50','spec_1'),
(5,'abondance', '< 5%','spec_1'),
(6,'abondance', '5-25%','spec_1'),
(7,'abondance', '16-25%','spec_1'),
(8,'abondance', '26-50%','spec_1'),
(9,'abondance', '51-75%','spec_1'),
(10,'abondance', '76-100%','spec_1'),
(NULL, 'nb_pied', '', 'spec_2'),
(1,'nb_pied_approx', '1 à 10','spec_3'),
(2,'nb_pied_approx', '10 à 100','spec_3'),
(3,'nb_pied_approx', 'Plus de 100','spec_3'),
(1,'stade_dev', 'Stade végétatif','spec_4'),
(2,'stade_dev', 'Stade bouton floraux', 'spec_4'),
(3,'stade_dev', 'Début floraison', 'spec_4'),
(4,'stade_dev', 'Pleine floraison', 'spec_4'),
(5,'stade_dev', 'Fin de floraison et maturation des fruits', 'spec_4'),
(6,'stade_dev', 'Dissémination', 'spec_4'),
(7,'stade_dev', 'Stade de décrépitude', 'spec_4');




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

CREATE OR REPLACE VIEW contact_faune.faune_poly AS 
 SELECT t.nom_vern,
    t.lb_nom,
    f.id_obs,
    f.id_synthese,
    f.observateur,
    f.date,
    f.cd_nom,
    f.insee,
    f.altitude,
    f.type_obs,
    f.effectif,
    f.comportement,
    f.nb_non_identife,
    f.nb_male,
    f.nb_femelle,
    f.nb_jeune,
    f.trace,
    f.commentaire,
    f.ccod_frt,
    f.geom_poly

   FROM contact_faune.releve f
   JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
   WHERE f.valide=true;


CREATE OR REPLACE VIEW contact_faune.faune_point AS 
 SELECT
    t.nom_vern,
    t.lb_nom,
    f.id_obs,
    f.id_synthese,
    f.observateur,
    f.date,
    f.cd_nom,
    f.insee,
    f.altitude,
    f.type_obs,
    f.effectif,
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
    f.geom_poly
   FROM contact_flore.releve f
     JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
     WHERE f.valide = true;


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
nom_structure character varying,
CONSTRAINT bib_structure_PK PRIMARY KEY (id_structure)
);

ALTER TABLE utilisateur.bib_structure
  OWNER TO onfuser;

INSERT INTO utilisateur.bib_structure
VALUES(1, 'ONF'), (2, 'Réserves');

CREATE TABLE utilisateur.bib_role(
auth_role integer,
descritption character varying,
CONSTRAINT bib_role_PK PRIMARY KEY (auth_role)
);

ALTER TABLE utilisateur.bib_role
  OWNER TO onfuser;


INSERT INTO utilisateur.bib_role
VALUES(1, 'lecteur'), (2, 'contributeur'), (3, 'administrateur');


--SPECIFIQUE DOM

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