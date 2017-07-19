CREATE TABLE synthese.releve
(
  id_synthese serial,
  id_lot integer,
  id_projet integer,
  id_sous_projet character varying(50),
  id_sous_projet_2 character varying(50),
  observateur text NOT NULL,
  date date NOT NULL,
  cd_nom integer NOT NULL,
  insee character varying(10),
  altitude integer,
  valide boolean,
  geom_point geometry(Point,32620),
  ccod_frt character varying(50),
  code_maille character varying,
  precision character varying,
  loc_exact boolean,
  id_structure integer,
  diffusable boolean,
  commentaire text,
  comm_loc text,
  CONSTRAINT synthese_pkey PRIMARY KEY (id_synthese),
  CONSTRAINT cd_nom FOREIGN KEY (cd_nom)
      REFERENCES taxonomie.taxref (cd_nom) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE SET NULL,
 CONSTRAINT code_maille_fk FOREIGN KEY (code_maille)
 	REFERENCES layers.maille_1_2 (id_maille) MATCH SIMPLE
 	ON UPDATE CASCADE,
 CONSTRAINT ccod_frt_fk FOREIGN KEY (ccod_frt)
      REFERENCES layers.perimetre_forets (ccod_frt) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION,
  CONSTRAINT insee_fk FOREIGN KEY (insee)
      REFERENCES layers.commune (code_insee) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION
);
ALTER TABLE synthese.releve
  OWNER TO onfuser;


CREATE TABLE contact_faune.releve
(
  id_obs serial NOT NULL,
  id_lot integer,
  id_synthese integer,
  id_projet integer,
  id_sous_projet character varying(50),
  id_sous_projet_2 character varying(50),
  observateur character varying(100) NOT NULL,
  date date NOT NULL,
  cd_nom integer NOT NULL,
  geom_point geometry(Point,32620),
  precision character varying,
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
  CONSTRAINT fa_id_synthese UNIQUE (id_synthese),
   CONSTRAINT code_maille_fk FOREIGN KEY (code_maille)
 	REFERENCES layers.maille_1_2 (id_maille) MATCH SIMPLE
 	ON UPDATE CASCADE,
 CONSTRAINT ccod_frt_fk FOREIGN KEY (ccod_frt)
      REFERENCES layers.perimetre_forets (ccod_frt) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION,
  CONSTRAINT insee_fk FOREIGN KEY (insee)
      REFERENCES layers.commune (code_insee) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION
);


ALTER TABLE contact_faune.releve
  OWNER TO onfuser;

CREATE TABLE contact_flore.releve
(
  id_obs serial NOT NULL,
  id_lot integer,
  id_synthese integer,
  id_projet integer,
  id_sous_projet character varying(50),
  id_sous_projet_2 character varying(50),
  observateur character varying(100) NOT NULL,
  date date NOT NULL,
  cd_nom integer NOT NULL,
  geom_point geometry(Point,32620),
  precision character varying,
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
  btn_floraux boolean,
  floraison boolean,
  fruit_maturation  boolean,
  dissemination boolean,
  stade_dev character varying (100),
  
  CONSTRAINT fl_pk PRIMARY KEY (id_obs),
  CONSTRAINT cd_nom FOREIGN KEY (cd_nom)
      REFERENCES taxonomie.taxref (cd_nom) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT fl_id_synthese UNIQUE (id_synthese),
   CONSTRAINT code_maille_fk FOREIGN KEY (code_maille)
 	REFERENCES layers.maille_1_2 (id_maille) MATCH SIMPLE
 	ON UPDATE CASCADE,
 CONSTRAINT ccod_frt_fk FOREIGN KEY (ccod_frt)
      REFERENCES layers.perimetre_forets (ccod_frt) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION,
  CONSTRAINT insee_fk FOREIGN KEY (insee)
      REFERENCES layers.commune (code_insee) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION
);
  ALTER TABLE contact_flore.releve
    OWNER TO onfuser;


  -- Trigger
-- create id_synthese in protocole

CREATE OR REPLACE FUNCTION synthese.tr_protocole_to_synthese() RETURNS TRIGGER AS $tr_protocole_to_synthese$
    DECLARE newid INTEGER;
    DECLARE protocoleid INTEGER;
    BEGIN
 
    INSERT INTO synthese.releve (id_projet, id_sous_projet, id_sous_projet_2, observateur, date, cd_nom, insee, ccod_frt, altitude, valide,geom_point, precision, loc_exact, code_maille, id_structure, diffusable) 
    VALUES( new.id_projet, new.id_sous_projet, new.id_sous_projet_2, new.observateur, new.date, new.cd_nom, new.insee, new.ccod_frt, new.altitude, new.valide, new.geom_point, new.precision, new.loc_exact, new.code_maille, new.id_structure, new.diffusable) RETURNING new.id_obs INTO protocoleid;
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

CREATE MATERIALIZED VIEW taxonomie.taxons_synthese AS 
 SELECT DISTINCT s.cd_nom,
    concat(t.lb_nom, ' = ', t.nom_complet_html) AS search_name,
    t.nom_valide,
    t.lb_nom,
    t.regne,
    s.id_projet
   FROM synthese.releve s
     JOIN taxonomie.taxref t ON t.cd_nom = s.cd_nom
UNION
 SELECT DISTINCT s.cd_nom,
    concat(t.nom_vern, ' = ', t.nom_complet_html) AS search_name,
    t.nom_valide,
    t.lb_nom,
    t.regne,
    s.id_projet
   FROM synthese.releve s
     JOIN taxonomie.taxref t ON t.cd_nom = s.cd_nom
  WHERE t.nom_vern IS NOT NULL
WITH DATA;

ALTER TABLE taxonomie.taxons_synthese
  OWNER TO onfuser;

CREATE TABLE synthese.bib_projet
(
  id_projet serial NOT NULL,
  nom_projet text,
  theme_principal character varying,
  service_onf character varying,
  partenaires character varying,
  subvention_commande character varying,
  duree integer,
  initiateur character varying,
  producteur character varying,
  commentaire text,
  table_independante boolean,
  saisie_possible boolean,
  nom_schema character varying,
  nom_table character varying,
  template character varying,
  bib_champs character varying,
  nom_bdd character varying,
  CONSTRAINT bib_projet_pk PRIMARY KEY (id_projet)
);
ALTER TABLE synthese.bib_projet
    OWNER TO onfuser;


--trigger pur raffraichir la vm taxonomie.taxons_synthese;
CREATE OR REPLACE FUNCTION synthese.refresh_taxons_synthese() RETURNS TRIGGER AS $refresh_taxons_synthese$
    BEGIN
 
   REFRESH MATERIALIZED VIEW taxonomie.taxons_synthese;
   RETURN NULL;
  
    END;
$refresh_taxons_synthese$ LANGUAGE plpgsql;


CREATE TRIGGER tr_refresh_vm_taxons_syntese
AFTER INSERT ON synthese.releve
    FOR EACH ROW EXECUTE PROCEDURE synthese.refresh_taxons_synthese();


INSERT INTO synthese.bib_projet(id_projet, nom_projet, table_independante, saisie_possible, nom_schema, nom_table, nom_bdd )
VALUES (99999, 'Tous les projets', FALSE, FALSE, 'synthese', 'releve', 'synthese');

INSERT INTO synthese.bib_projet (nom_projet, saisie_possible, table_independante, service_onf, producteur, nom_schema, nom_table, template, nom_bdd, bib_champs ) VALUES 
  ('Contact Flore', TRUE, TRUE, 'Tous', 'ONF', 'contact_flore', 'releve', 'addObs/contact_flore.html', 'contact_flore', 'contact_flore.bib_champs_contact_flore'),
  ('Contact Faune', TRUE, TRUE, 'Tous', 'ONF', 'contact_faune', 'releve', 'addObs/contact_faune.html', 'contact_faune', 'contact_faune.bib_champs_contact_faune');

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
(8,'trace', '{"values":["Crottes ou crottier", "Ecorçage ou frottis", "Empreintes", "Epiderme", "Guano", "Nid", "Oeufs", "Pelage", "Pelotes de réjection", "Restes alimentaires", "Restes de l''animal", "Terrier", "Larves", "Exuvie"]}' ,'spec_8', 'Trace', 'select');





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
(4,'btn_floraux', '{"values":[]}','spec_4', 'Boutons floraux', 'checkbox'),
(5,'floraison', '{"values":[]}', 'spec_5', 'Floraison', 'checkbox'),
(6,'fruit_maturation','{"values":[]}', 'spec_6', 'Fruit mature', 'checkbox' ),
(7,'dissemination', '{"values":[]}', 'spec_7' ,'Dissémination', 'checkbox' );



--SPECIFIQUE DOM

--liste rouge regionale
CREATE TABLE taxonomie.liste_rouge_reg(
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

ALTER TABLE taxonomie.liste_rouge_reg
OWNER TO onfuser;


COPY taxonomie.liste_rouge_reg
FROM E'/tmp/Liste_rouge_regionale.csv'
WITH (format 'csv', header 'true', delimiter E';');



  -- Creation des vues pour les exports en shapefile

CREATE OR REPLACE VIEW contact_faune.layer_poly AS 
 SELECT 
    f.id_projet,
    t.nom_vern,
    t.lb_nom,
    f.observateur,
    f.date,
    ST_X(ST_CENTROID(ST_TRANSFORM(m.geom,4326))) AS X,
    ST_Y(ST_CENTROID(ST_TRANSFORM(m.geom,4326))) AS Y,
    f.precision,
    f.cd_nom,
    f.insee,
    f.altitude,
    f.commentaire,
    f.comm_loc,
    f.ccod_frt,
    m.geom,
    m.id_maille,
    s.nom_organisme,
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
   JOIN layers.maille_1_2 m ON m.id_maille::text = f.code_maille::text 
   LEFT JOIN utilisateurs.bib_organismes s ON f.id_structure = s.id_organisme
   WHERE f.valide=true AND loc_exact = false;

   ALTER VIEW contact_faune.layer_poly
  OWNER TO onfuser;


CREATE OR REPLACE VIEW contact_faune.layer_point AS 
 SELECT 
    f.id_projet,
    t.nom_vern,
    t.lb_nom,
    f.observateur,
    f.date,
    ST_X(ST_TRANSFORM(f.geom_point, 4326)) AS X,
    ST_Y(ST_TRANSFORM(f.geom_point, 4326)) AS Y,
    f.precision,
    f.comm_loc,
    f.cd_nom,
    f.insee,
    f.ccod_frt,
    f.altitude,
    f.commentaire,
    f.geom_point,
    s.nom_organisme,
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
   LEFT JOIN utilisateurs.bib_organismes s ON f.id_structure = s.id_organisme
  WHERE f.valide=true AND f.loc_exact = TRUE;

  ALTER VIEW contact_faune.layer_point
  OWNER TO onfuser;

  CREATE OR REPLACE VIEW contact_flore.layer_point AS 
 SELECT 
    f.id_projet,
    t.nom_vern,
    t.lb_nom,
    f.observateur,
    f.date,
    ST_X(ST_TRANSFORM(f.geom_point, 4326)) AS X,
    ST_Y(ST_TRANSFORM(f.geom_point, 4326)) AS Y,
    f.precision,
    f.comm_loc,
    f.cd_nom,
    f.insee,
    f.ccod_frt,
    f.altitude,
    f.geom_point,
    f.commentaire,
    s.nom_organisme,
    f.id_structure,
    f.id_synthese,
    f.nb_pied_approx,
    f.nb_pied,
    f.btn_floraux,
    f.floraison ,
    f.fruit_maturation ,
    f.dissemination,
    f.stade_dev


   FROM contact_flore.releve f
   JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
   LEFT JOIN utilisateurs.bib_organismes s ON f.id_structure = s.id_organisme
  WHERE f.loc_exact = TRUE AND f.valide = TRUE;

  ALTER VIEW contact_flore.layer_point
  OWNER TO onfuser;



CREATE OR REPLACE VIEW contact_flore.layer_poly AS 
 SELECT 
    f.id_projet,
    t.nom_vern,
    t.lb_nom,
    f.id_obs,
    f.observateur,
    f.date,
    ST_X(ST_CENTROID(ST_TRANSFORM(m.geom,4326))) AS X,
    ST_Y(ST_CENTROID(ST_TRANSFORM(m.geom,4326))) AS Y,
    f.precision,
    f.comm_loc,
    f.cd_nom,
    f.insee,
    f.ccod_frt,
    f.altitude,
    f.commentaire,
    m.geom,
    m.id_maille,
    s.nom_organisme,
    f.id_structure,
    f.id_synthese,
    f.btn_floraux,
    f.floraison ,
    f.fruit_maturation ,
    f.dissemination,
    f.nb_pied_approx,
    f.nb_pied,
    f.stade_dev

   FROM contact_flore.releve f
    JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
    JOIN layers.maille_1_2 m ON m.id_maille::text = f.code_maille::text
    LEFT JOIN utilisateurs.bib_organismes s ON f.id_structure = s.id_organisme
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
             JOIN layers.maille_1_2 m ON m.id_maille::text = fm.code_maille::text
          WHERE fm.loc_exact = false
        )
 SELECT
    f.id_projet,
    t.nom_vern,
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
    f.precision,
    f.loc_exact,
    f.comm_loc,
    f.cd_nom,
    f.insee,
    f.ccod_frt,
    f.altitude,
    f.geom_point,
    f.commentaire,
    s.nom_organisme,
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
     LEFT JOIN utilisateurs.bib_organismes s ON f.id_structure = s.id_organisme;

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
             JOIN layers.maille_1_2 m ON m.id_maille::text = fm.code_maille::text
          WHERE fm.loc_exact = false
        )
 SELECT
    f.id_projet,
    t.nom_vern,
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
    f.precision,
    f.loc_exact,
    f.comm_loc,
    f.cd_nom,
    f.insee,
    f.ccod_frt,
    f.altitude,
    f.geom_point,
    f.commentaire,
    s.nom_organisme,
    f.id_structure,
    f.id_synthese,
    f.btn_floraux,
    f.floraison ,
    f.fruit_maturation ,
    f.dissemination,
    f.nb_pied_approx,
    f.nb_pied,
    f.stade_dev
   FROM contact_flore.releve f
     JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
     LEFT JOIN coord_point cp ON cp.id_obs = f.id_obs
     LEFT JOIN coord_maille cm ON cm.id_obs = f.id_obs
     LEFT JOIN utilisateurs.bib_organismes s ON f.id_structure = s.id_organisme;

ALTER TABLE contact_flore.to_csv
  OWNER TO onfuser;


CREATE OR REPLACE VIEW synthese.layer_poly AS 
 SELECT 
    f.id_projet,
    t.nom_vern,
    t.lb_nom,
    f.observateur,
    f.date,
    ST_X(ST_CENTROID(ST_TRANSFORM(m.geom,4326))) AS X,
    ST_Y(ST_CENTROID(ST_TRANSFORM(m.geom,4326))) AS Y,
    f.precision,
    f.cd_nom,
    f.insee,
    f.ccod_frt,
    f.altitude,
    m.geom,
    m.id_maille,
    s.nom_organisme,
    f.id_structure,
    f.id_synthese

   FROM synthese.releve f
    JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
    JOIN layers.maille_1_2 m ON m.id_maille::text = f.code_maille::text
    LEFT JOIN utilisateurs.bib_organismes s ON f.id_structure = s.id_organisme
     WHERE f.valide = TRUE AND f.loc_exact = FALSE;

    ALTER VIEW synthese.layer_poly
    OWNER TO onfuser;

  CREATE OR REPLACE VIEW synthese.layer_point AS 
 SELECT 
    f.id_projet,
    t.nom_vern,
    t.lb_nom,
    f.observateur,
    f.date,
    ST_X(ST_TRANSFORM(f.geom_point, 4326)) AS X,
    ST_Y(ST_TRANSFORM(f.geom_point, 4326)) AS Y,
    f.precision,
    f.cd_nom,
    f.insee,
    f.ccod_frt,
    f.altitude,
    f.geom_point,
    s.nom_organisme,
    f.id_structure,
    f.id_synthese


   FROM synthese.releve f
   JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
   LEFT JOIN utilisateurs.bib_organismes s ON f.id_structure = s.id_organisme
  WHERE f.loc_exact = TRUE AND f.valide = TRUE;

  ALTER VIEW synthese.layer_point
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
             JOIN layers.maille_1_2 m ON m.id_maille::text = fm.code_maille::text
          WHERE fm.loc_exact = false
        )
 SELECT
    f.id_projet,
    p.nom_projet,
    t.nom_vern,
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
    f.precision,
    f.loc_exact,
    f.cd_nom,
    f.insee,
    f.ccod_frt,
    f.altitude,
    f.geom_point,
    s.nom_organisme,
    f.id_structure,
    f.id_synthese
   FROM synthese.releve f
     JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
     LEFT JOIN coord_point cp ON cp.id_synthese = f.id_synthese
     LEFT JOIN coord_maille cm ON cm.id_synthese = f.id_synthese
     LEFT JOIN utilisateurs.bib_organismes s ON f.id_structure = s.id_organisme
     JOIN synthese.bib_projet p ON p.id_projet = f.id_projet;

ALTER TABLE synthese.to_csv
  OWNER TO onfuser;


CREATE TABLE import (
unique_id serial,
id_obs integer,
id_projet integer,
id_sous_projet character varying,
id_sous_projet_2 character varying,
x float,
y float,
cd_ref integer,
taxon_valide text,
precision character varying,
observateur character varying,
date date,
publication character varying,
auteurs_publication character varying,
collections character varying,
phenologie character varying,
nombre integer,
commentaire character varying,
CONSTRAINT unique_id_pk PRIMARY KEY (unique_id)
);


CREATE TABLE ip_connexion(
id serial CONSTRAINT ip_connexion_pk PRIMARY KEY,
ip character varying
);

ALTER TABLE ip_connexion 
OWNER TO onfuser;







