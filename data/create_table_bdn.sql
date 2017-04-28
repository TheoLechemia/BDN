CREATE TABLE synthese.releve
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
  code_maille character varying,
  loc_exact boolean,
  id_structure integer,
  diffusable boolean,
  CONSTRAINT synthese_pkey PRIMARY KEY (id_synthese),
  CONSTRAINT cd_nom FOREIGN KEY (cd_nom)
      REFERENCES taxonomie.taxref (cd_nom) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE SET NULL
);
ALTER TABLE synthese.releve
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
  code_maille character varying,
  id_structure integer,
  diffusable boolean,
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
  code_maille character varying,
  id_structure integer,
  diffusable boolean,
  nb_pied_approx character varying(15),
  nb_pied integer,
  boutons_flo boolean,
  floraison boolean,
  fruit_maturation  boolean,
  dissemination boolean,
  stade_dev character varying (100),
  
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
 
    INSERT INTO synthese.releve (protocole, observateur, date, cd_nom, insee, ccod_frt, altitude, valide,geom_point, loc_exact, code_maille, id_structure, diffusable) 
    VALUES(tg_table_schema, new.observateur, new.date, new.cd_nom, new.insee, new.ccod_frt, new.altitude, new.valide, new.geom_point, new.loc_exact, new.code_maille, new.id_structure, new.diffusable) RETURNING new.id_obs INTO protocoleid;
    SELECT INTO newid currval('synthese.releve_id_synthese_seq');
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
    s.protocole,
    t.nom_vern,
    t.lb_nom,
    t.regne
   FROM synthese.releve s
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


INSERT INTO synthese.bib_protocole VALUES
 ('Contact Flore', 'contact_flore', 'releve', 'contact_flore.releve', 'addObs/contactFlore.html', 'contact_flore.bib_champs_contact_flore'),
  ('Contact Faune','contact_faune', 'releve', 'contact_faune.releve', 'addObs/contactFaune.html', 'contact_faune.bib_champs_contact_faune');

CREATE TABLE contact_faune.bib_champs_contact_faune(
id_champ integer CONSTRAINT bib_fa_primary_key PRIMARY KEY,
no_spec character varying,
nom_champ character varying,
valeur text,
lib_champ character varying,
type_widget character varying
);
ALTER TABLE contact_faune.bib_champs_contact_faune
    OWNER TO onfuser;



INSERT INTO contact_faune.bib_champs_contact_faune (id_champ, nom_champ, valeur, no_spec, lib_champ, type_widget) VALUES
(1,'type_obs', '{"values": ["Contact visuel","Chant", "Cris", "Autre contact sonore","Nid", "Gîte", "Nichoir", "Empreintes", "Détection", "Indices (crottes,...)" ]}', 'spec_1', 'Type d''observation', 'select'),
(2,'effectif', '{"values": ["1-5", "6-10", "11-20", "21-50", "51-100", "101-500", "501-1000", ">1000"]}', 'spec_2', 'Effectif', 'select'),
(3,'comportement', '{"values": ["Reproduction", "Parade nuptiale", "Ponte", "Nidification", "Emergence", "Eclosion", "Comportement parental", "Colonie avec mise bas", "Colonie de reproduction", "Colonie avec certaines femelles gestantes", "Colonie avec jeunes non volants", "Colonie avec jeunes volants", "Colonie sans jeunes", "Colonie avec males", "Individus isolés", "En chasse", "En vol", "Fuite", "Alerte", "Repos", "Léthargie diurne", "Alimentation", "Transit", "Estivage", "Migration", "Harem", "Autres"]}','spec_3', 'Comportement', 'select'),
(4, 'nb_male', '{"values":[]}', 'spec_4', 'Nombre de mâle', 'number'),
(5, 'nb_femelle', '{"values":[]}', 'spec_5', 'Nombre de femelle', 'number'),
(6, 'nb_jeune', '{"values":[]}', 'spec_6', 'Nombre de jeune', 'number'),
(7, 'nb_non_identife', '{"values":[]}', 'spec_7', 'Nombre non identifie', 'number'),
(8,'trace', '{"values":["Crottes ou crottier", "Ecorçage ou frottis", "Empreintes", "Epiderme", "Guano", "Nid", "Oeufs", "Pelage", "Pelotes de réjection", "Restes alimentaires", "Restes de l''animal", "Terrier", "Larves", "Exuvie"]}' ,'spec_8', 'Trace', 'select')





CREATE TABLE contact_flore.bib_champs_contact_flore(
id_champ integer CONSTRAINT bib_fa_primary_key PRIMARY KEY,
no_spec character varying,
nom_champ character varying,
valeur text,
lib_champ character varying,
type_widget character varying
);
ALTER TABLE contact_flore.bib_champs_contact_flore
    OWNER TO onfuser;

INSERT INTO contact_flore.bib_champs_contact_flore (id_champ, nom_champ, valeur, no_spec, lib_champ, type_widget) VALUES
(1, 'nb_pied', '{"values":[]}', 'spec_1', 'Nombre de pied', 'number'),
(2,'nb_pied_approx', '{"values":["1 à 10", "11 à 100", "Plus de 100"]}' ,'spec_2', 'Nombre de pied approximatif', 'select'),
(3,'stade_dev', '{"values":["Juvénile", "Adulte", "Sénéscent"]}','spec_3', 'Stade de développement', 'select'),
(4,'boutons_flo', '{"values":[]}','spec_4', 'Boutons floraux', 'checkbox'),
(5,'floraison', '{"values":[]}', 'spec_5', 'Floraison', 'checkbox'),
(6,'fruit_maturation','{"values":[]}', 'spec_6', 'Fruit mature', 'checkbox' ),
(7,'dissemination', '{"values":[]}', 'spec_7' ,'Dissémination', 'checkbox' );






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
--CREATE VIEW taxonomie.taxons_contact_flore AS(
--SELECT taxonomie.find_cdref(cd_nom) AS cd_ref, nom_vern, lb_nom
--FROM taxonomie.import_taxref
--WHERE (mar != 'A' OR gua != 'A' OR sm != 'A' OR sb != 'A') AND regne = 'Plantae'
--);

CREATE MATERIALIZED VIEW taxonomie.taxons_contact_faune AS (

SELECT taxonomie.find_cdref(t3.cd_nom) AS cd_ref,nom_valide, CONCAT(t3.lb_nom, ' = ', t3.nom_complet_html) AS search_name
from taxonomie.cor_nom_liste t1
JOIN taxonomie.bib_noms t2 ON t1.id_nom = t2.id_nom
JOIN taxonomie.taxref t3 ON t3.cd_nom = t2.cd_nom
WHERE t1.id_liste = 1001

UNION
SELECT taxonomie.find_cdref(t3.cd_nom),nom_valide, CONCAT(t3.nom_vern, ' = ', t3.nom_complet_html) AS search_name
from taxonomie.cor_nom_liste t1
JOIN taxonomie.bib_noms t2 ON t1.id_nom = t2.id_nom
JOIN taxonomie.taxref t3 ON t3.cd_nom = t2.cd_nom
WHERE t1.id_liste = 1001 AND t3.nom_vern IS NOT NULL
);

ALTER TABLE taxonomie.taxons_contact_faune
  OWNER TO onfuser;

--CREATE VIEW taxonomie.taxons_contact_faune AS(
--SELECT taxonomie.find_cdref(cd_nom) AS cd_ref, nom_vern, lb_nom
--FROM taxonomie.import_taxref
--WHERE (mar != 'A' OR gua != 'A' OR sm != 'A' OR sb != 'A') AND regne = 'Animalia'
--);
CREATE MATERIALIZED VIEW taxonomie.taxons_contact_flore AS (

SELECT taxonomie.find_cdref(t3.cd_nom) AS cd_ref, nom_valide, CONCAT(t3.lb_nom, ' = ', t3.nom_complet_html) AS search_name
from taxonomie.cor_nom_liste t1
JOIN taxonomie.bib_noms t2 ON t1.id_nom = t2.id_nom
JOIN taxonomie.taxref t3 ON t3.cd_nom = t2.cd_nom
WHERE t1.id_liste = 1002

UNION
SELECT taxonomie.find_cdref(t3.cd_nom),nom_valide, CONCAT(t3.nom_vern, ' = ', t3.nom_complet_html) AS search_name
from taxonomie.cor_nom_liste t1
JOIN taxonomie.bib_noms t2 ON t1.id_nom = t2.id_nom
JOIN taxonomie.taxref t3 ON t3.cd_nom = t2.cd_nom
WHERE t1.id_liste = 1002 AND t3.nom_vern IS NOT NULL
);

ALTER TABLE taxonomie.taxons_contact_flore
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



  -- Creation des vues pour les exports en shapefile

CREATE OR REPLACE VIEW contact_faune.layer_poly AS 
 SELECT 
    t.nom_vern,
    t.lb_nom,
    f.observateur,
    f.date,
    ST_X(ST_CENTROID(ST_TRANSFORM(m.geom,4326))) AS X,
    ST_Y(ST_CENTROID(ST_TRANSFORM(m.geom,4326))) AS Y,
    f.cd_nom,
    f.insee,
    f.altitude,
    f.commentaire,
    f.comm_loc,
    f.ccod_frt,
    m.geom,
    m.code_1km,
    s.nom_structure,
    f.id_structure,
    f.id_synthese,
    f.type_obs,
    f.effectif,
    f.comportement,
    f.nb_non_identife,
    f.nb_male,
    f.nb_femelle,
    f.nb_jeune,
    f.trace


   FROM contact_faune.releve f
   JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
   JOIN layers.mailles_1k m ON m.code_1km::text = f.code_maille::text 
   JOIN utilisateur.bib_structure s ON f.id_structure = s.id_structure
   WHERE f.valide=true AND loc_exact = false;

   ALTER VIEW contact_faune.layer_poly
  OWNER TO onfuser;


CREATE OR REPLACE VIEW contact_faune.layer_point AS 
 SELECT 
    t.nom_vern,
    t.lb_nom,
    f.observateur,
    f.date,
    ST_X(ST_TRANSFORM(f.geom_point, 4326)) AS X,
    ST_Y(ST_TRANSFORM(f.geom_point, 4326)) AS Y,
    f.comm_loc,
    f.cd_nom,
    f.insee,
    f.ccod_frt,
    f.altitude,
    f.commentaire,
    f.geom_point,
    s.nom_structure,
    f.id_structure,
    f.id_synthese,
    f.type_obs,
    f.effectif,
    f.comportement,
    f.nb_non_identife,
    f.nb_male,
    f.nb_femelle,
    f.nb_jeune,
    f.trace


    
   FROM contact_faune.releve f
   JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
   JOIN utilisateur.bib_structure s ON f.id_structure = s.id_structure
  WHERE f.valide=true AND f.loc_exact = TRUE;

  ALTER VIEW contact_faune.layer_point
  OWNER TO onfuser;

  CREATE OR REPLACE VIEW contact_flore.layer_point AS 
 SELECT 
    t.nom_vern,
    t.lb_nom,
    f.observateur,
    f.date,
    ST_X(ST_TRANSFORM(f.geom_point, 4326)) AS X,
    ST_Y(ST_TRANSFORM(f.geom_point, 4326)) AS Y,
    f.comm_loc,
    f.cd_nom,
    f.insee,
    f.ccod_frt,
    f.altitude,
    f.geom_point,
    f.commentaire,
    s.nom_structure,
    f.id_structure,
    f.id_synthese,
    f.abondance,
    f.nb_pied_approx,
    f.nb_pied,
    f.stade_dev


   FROM contact_flore.releve f
   JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
   JOIN utilisateur.bib_structure s ON f.id_structure = s.id_structure
  WHERE f.loc_exact = TRUE AND f.valide = TRUE;

  ALTER VIEW contact_flore.layer_point
  OWNER TO onfuser;



CREATE OR REPLACE VIEW contact_flore.layer_poly AS 
 SELECT 
    t.nom_vern,
    t.lb_nom,
    f.id_obs,
    f.observateur,
    f.date,
    ST_X(ST_CENTROID(ST_TRANSFORM(m.geom,4326))) AS X,
    ST_Y(ST_CENTROID(ST_TRANSFORM(m.geom,4326))) AS Y,
    f.comm_loc,
    f.cd_nom,
    f.insee,
    f.ccod_frt,
    f.altitude,
    f.commentaire,
    m.geom,
    m.code_1km,
    s.nom_structure,
    f.id_structure,
    f.id_synthese,
    f.abondance,
    f.nb_pied_approx,
    f.nb_pied,
    f.stade_dev

   FROM contact_flore.releve f
    JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
    JOIN layers.mailles_1k m ON m.code_1km::text = f.code_maille::text
    JOIN utilisateur.bib_structure s ON f.id_structure = s.id_structure
     WHERE f.valide = TRUE AND f.loc_exact = FALSE;

    ALTER VIEW contact_flore.layer_poly
    OWNER TO onfuser;

CREATE OR REPLACE VIEW contact_faune.to_csv AS 
 WITH coord_point AS (
         SELECT fp.id_obs,
            st_x(st_transform(fp.geom_point, 4326)) AS x,
            st_y(st_transform(fp.geom_point, 4326)) AS y
           FROM contact_faune.releve fp
          WHERE fp.loc_exact = true
        ), coord_maille AS (
         SELECT fm.id_obs,
            fm.code_maille,
            st_x(st_centroid(st_transform(m.geom, 4326))) AS x,
            st_y(st_centroid(st_transform(m.geom, 4326))) AS y
           FROM contact_faune.releve fm
             JOIN layers.mailles_1k m ON m.code_1km::text = fm.code_maille::text
          WHERE fm.loc_exact = false
        )
 SELECT t.nom_vern,
    t.lb_nom,
    f.observateur,
    f.date,
        CASE f.loc_exact
            WHEN true THEN cp.x
            WHEN false THEN cm.x
            ELSE NULL::double precision
        END AS x,
        CASE f.loc_exact
            WHEN true THEN cp.y
            WHEN false THEN cm.y
            ELSE NULL::double precision
        END AS y,
    f.loc_exact,
    f.comm_loc,
    f.cd_nom,
    f.insee,
    f.ccod_frt,
    f.altitude,
    f.geom_point,
    f.commentaire,
    s.nom_structure,
    f.id_structure,
    f.id_synthese,
    f.type_obs,
    f.effectif,
    f.comportement,
    f.nb_non_identife,
    f.nb_male,
    f.nb_femelle,
    f.nb_jeune,
    f.trace
   FROM contact_faune.releve f
     JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
     LEFT JOIN coord_point cp ON cp.id_obs = f.id_obs
     LEFT JOIN coord_maille cm ON cm.id_obs = f.id_obs
     JOIN utilisateur.bib_structure s ON f.id_structure = s.id_structure;

ALTER TABLE contact_faune.to_csv
  OWNER TO onfuser;



CREATE OR REPLACE VIEW contact_flore.to_csv AS 
 WITH coord_point AS (
         SELECT fp.id_obs,
            st_x(st_transform(fp.geom_point, 4326)) AS x,
            st_y(st_transform(fp.geom_point, 4326)) AS y
           FROM contact_flore.releve fp
          WHERE fp.loc_exact = true
        ), coord_maille AS (
         SELECT fm.id_obs,
            fm.code_maille,
            st_x(st_centroid(st_transform(m.geom, 4326))) AS x,
            st_y(st_centroid(st_transform(m.geom, 4326))) AS y
           FROM contact_flore.releve fm
             JOIN layers.mailles_1k m ON m.code_1km::text = fm.code_maille::text
          WHERE fm.loc_exact = false
        )
 SELECT t.nom_vern,
    t.lb_nom,
    f.observateur,
    f.date,
        CASE f.loc_exact
            WHEN true THEN cp.x
            WHEN false THEN cm.x
            ELSE NULL::double precision
        END AS x,
        CASE f.loc_exact
            WHEN true THEN cp.y
            WHEN false THEN cm.y
            ELSE NULL::double precision
        END AS y,
    f.loc_exact,
    f.comm_loc,
    f.cd_nom,
    f.insee,
    f.ccod_frt,
    f.altitude,
    f.geom_point,
    f.commentaire,
    s.nom_structure,
    f.id_structure,
    f.id_synthese,
    f.abondance,
    f.nb_pied_approx,
    f.nb_pied,
    f.stade_dev
   FROM contact_flore.releve f
     JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
     LEFT JOIN coord_point cp ON cp.id_obs = f.id_obs
     LEFT JOIN coord_maille cm ON cm.id_obs = f.id_obs
     JOIN utilisateur.bib_structure s ON f.id_structure = s.id_structure;

ALTER TABLE contact_flore.to_csv
  OWNER TO onfuser;



CREATE OR REPLACE VIEW synthese.to_csv AS 
 WITH coord_point AS (
         SELECT fp.id_synthese,
            st_x(st_transform(fp.geom_point, 4326)) AS x,
            st_y(st_transform(fp.geom_point, 4326)) AS y
           FROM synthese.releve fp
          WHERE fp.loc_exact = true
        ), coord_maille AS (
         SELECT fm.id_synthese,
            fm.code_maille,
            st_x(st_centroid(st_transform(m.geom, 4326))) AS x,
            st_y(st_centroid(st_transform(m.geom, 4326))) AS y
           FROM synthese.releve fm
             JOIN layers.mailles_1k m ON m.code_1km::text = fm.code_maille::text
          WHERE fm.loc_exact = false
        )
 SELECT t.nom_vern,
    t.lb_nom,
    f.observateur,
    f.date,
        CASE f.loc_exact
            WHEN true THEN cp.x
            WHEN false THEN cm.x
            ELSE NULL::double precision
        END AS x,
        CASE f.loc_exact
            WHEN true THEN cp.y
            WHEN false THEN cm.y
            ELSE NULL::double precision
        END AS y,
    f.loc_exact,
    f.cd_nom,
    f.insee,
    f.ccod_frt,
    f.altitude,
    f.geom_point,
    s.nom_structure,
    f.id_structure,
    f.id_synthese
   FROM synthese.releve f
     JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
     LEFT JOIN coord_point cp ON cp.id_synthese = f.id_synthese
     LEFT JOIN coord_maille cm ON cm.id_synthese = f.id_synthese
     JOIN utilisateur.bib_structure s ON f.id_structure = s.id_structure;

ALTER TABLE synthese.to_csv
  OWNER TO onfuser;
