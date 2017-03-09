CREATE TABLE bdn.synthese
(
  id_synthese character varying(15) NOT NULL,
  protocole character varying(50) NOT NULL,
  observateur character varying(100) NOT NULL,
  date date NOT NULL,
  cd_nom integer NOT NULL,
  insee character varying(10),
  altitude integer,
  valide boolean,
  id_kfey integer,
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
ALTER TABLE bdn.synthese
  OWNER TO onfuser;


CREATE TABLE bdn.faune
(
  id_obs serial NOT NULL,
  id_synthese character varying(15),
  protocole character varying(50) NOT NULL,
  observateur character varying(100) NOT NULL,
  date date NOT NULL,
  cd_nom integer NOT NULL,
  insee character varying(10),
  altitude integer,
  type_obs character varying(50),
  nb_individu_approx character varying(50),
  comportement character varying(50),
  nb_non_identife integer,
  nb_male integer,
  nb_femelle integer,
  nb_jeune integer,
  trace character varying(50),
  geom_point geometry(Point,32620),
  commentaire character varying(150),
  valide boolean,
  ccod_frt character varying(50),
  loc_exact boolean,
  code_maille character varying(20),
  id_structure integer,
  CONSTRAINT faune_pkey PRIMARY KEY (id_obs),
  CONSTRAINT cd_nom FOREIGN KEY (cd_nom)
      REFERENCES taxonomie.taxref (cd_nom) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT fa_id_synthese UNIQUE (id_synthese)
);


ALTER TABLE bdn.faune
  OWNER TO onfuser;

CREATE TABLE bdn.flore
(
  id_obs serial NOT NULL,
  id_synthese character varying(15),
  protocole character varying(50) NOT NULL,
  observateur character varying(100) NOT NULL,
  date date NOT NULL,
  cd_nom integer NOT NULL,
  insee character varying(10),
  altitude integer,
  abondance character varying(15),
  nb_pied_approx character varying(15),
  nb_pied integer,
  stade_dev character varying(50),
  geom_point geometry(Point,32620),
  commentaire character varying(150),
  valide boolean,
  ccod_frt character varying(50),
  loc_exact boolean,
  code_maille character varying(20),
  id_structure integer,
  CONSTRAINT flore_pkey PRIMARY KEY (id_obs),
  CONSTRAINT cd_nom FOREIGN KEY (cd_nom)
      REFERENCES taxonomie.taxref (cd_nom) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT fl_id_synthese UNIQUE (id_synthese)
);
  ALTER TABLE bdn.flore
    OWNER TO onfuser;


  -- Trigger
-- create id_synthese in protocole

--flore
CREATE OR REPLACE FUNCTION bdn.fill_id_synthese_flore() RETURNS TRIGGER AS $fill_id_synthese$
    BEGIN
    UPDATE bdn.flore
    SET id_synthese = concat_ws('', LEFT(protocole,2)::text, id_obs::text);
    RETURN NULL;
    END;
$fill_id_synthese$ LANGUAGE plpgsql;

CREATE TRIGGER tr_id_synthese_fl
AFTER INSERT ON bdn.flore
    FOR EACH ROW EXECUTE PROCEDURE bdn.fill_id_synthese_flore();



CREATE OR REPLACE FUNCTION bdn.fill_id_synthese_faune() RETURNS TRIGGER AS $fill_id_synthese$
    BEGIN
    UPDATE bdn.faune
    SET id_synthese = concat_ws('', LEFT(protocole,2)::text, id_obs::text);
    RETURN NULL;
    END;
$fill_id_synthese$ LANGUAGE plpgsql;

CREATE TRIGGER tr_id_synthese_fa
AFTER INSERT ON bdn.faune
    FOR EACH ROW EXECUTE PROCEDURE bdn.fill_id_synthese_faune();


CREATE OR REPLACE FUNCTION bdn.tr_protocole_to_synthese() RETURNS TRIGGER AS $tr_protocole_to_synthese$
    BEGIN
    INSERT INTO bdn.synthese (id_synthese, protocole, observateur, date, cd_nom, insee, ccod_frt, altitude, valide,geom_point, loc_exact, code_maille, id_structure) 
    VALUES( concat_ws('', LEFT(new.protocole,2)::text, new.id_obs::text), new.protocole, new.observateur, new.date, new.cd_nom, new.insee, new.ccod_frt, new.altitude, new.valide, new.geom_point, new.loc_exact, new.code_maille, new.id_structure);
    RETURN NEW;
  
    END;
$tr_protocole_to_synthese$ LANGUAGE plpgsql;

CREATE TRIGGER tr_fl_to_synthese
BEFORE INSERT ON bdn.flore
    FOR EACH ROW EXECUTE PROCEDURE bdn.tr_protocole_to_synthese();

CREATE TRIGGER tr_fa_to_synthese
BEFORE INSERT ON bdn.faune
    FOR EACH ROW EXECUTE PROCEDURE bdn.tr_protocole_to_synthese();


CREATE OR REPLACE VIEW bdn.v_search_taxons AS 
 SELECT DISTINCT s.cd_nom,
    t.nom_vern,
    t.lb_nom,
    s.protocole
   FROM bdn.synthese s
     JOIN taxonomie.taxref t ON s.cd_nom = t.cd_nom;

ALTER TABLE bdn.v_search_taxons
  OWNER TO onfuser;



-- Taxonomie

--habitat du taxref
CREATE TABLE taxonomie.bib_habitat (
id integer,
type character varying
);

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
CREATE VIEW taxonomie.taxons_flore AS(
SELECT taxonomie.find_cdref(cd_nom) AS cd_ref, nom_vern, lb_nom
FROM taxonomie.taxref
WHERE (mar != 'A' OR gua != 'A' OR sm != 'A' OR sb != 'A') AND regne = 'Plantae'
);

ALTER TABLE taxonomie.taxons_flore
  OWNER TO onfuser;

CREATE VIEW taxonomie.taxons_faune AS(
SELECT taxonomie.find_cdref(cd_nom) AS cd_ref, nom_vern, lb_nom
FROM taxonomie.taxref
WHERE (mar != 'A' OR gua != 'A' OR sm != 'A' OR sb != 'A') AND regne = 'Animalia'
);

ALTER TABLE taxonomie.taxons_faune
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


CREATE OR REPLACE VIEW bdn.faune_point AS 
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

   FROM bdn.faune f
   JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
  WHERE f.loc_exact = true;

  CREATE OR REPLACE VIEW bdn.flore_point AS 
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

   FROM bdn.flore flore
   JOIN taxonomie.taxref t ON t.cd_nom = flore.cd_nom
  WHERE flore.loc_exact = true AND flore.valide = true;

  CREATE OR REPLACE VIEW bdn.flore_poly AS 
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

   FROM bdn.flore f
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