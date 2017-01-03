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
  CONSTRAINT faune_pkey PRIMARY KEY (id_obs),
  CONSTRAINT id_synthese FOREIGN KEY (id_synthese)
      REFERENCES bdn.synthese (id_synthese) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT cd_nom FOREIGN KEY (cd_nom)
      REFERENCES taxonomie.taxref_v10 (cd_nom) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT fa_id_synthese UNIQUE (id_synthese)
);
WITH (
  OIDS=FALSE
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
  CONSTRAINT flore_pkey PRIMARY KEY (id_obs),
  CONSTRAINT cd_nom FOREIGN KEY (cd_nom)
      REFERENCES taxonomie.taxref (cd_nom) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT id_synthese FOREIGN KEY (id_synthese)
      REFERENCES bdn.synthese (id_synthese) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fl_id_synthese UNIQUE (id_synthese)
)
ALTER TABLE bdn.flore
  OWNER TO onfuser;


  -- Trigger
-- create id_synthese in protocole

--flore
CREATE OR REPLACE FUNCTION fill_id_synthese_flore() RETURNS TRIGGER AS $fill_id_synthese$
    BEGIN
    UPDATE bdn.flore
    SET id_synthese = concat_ws('', LEFT(protocole,2)::text, id_obs::text);
    RETURN NULL;
    END;
$fill_id_synthese$ LANGUAGE plpgsql;

CREATE TRIGGER tr_id_synthese_fl
AFTER INSERT ON bdn.faune
    FOR EACH ROW EXECUTE PROCEDURE fill_id_synthese_flore();



CREATE OR REPLACE FUNCTION fill_id_synthese_faune() RETURNS TRIGGER AS $fill_id_synthese$
    BEGIN
    UPDATE bdn.faune
    SET id_synthese = concat_ws('', LEFT(protocole,2)::text, id_obs::text);
    RETURN NULL;
    END;
$fill_id_synthese$ LANGUAGE plpgsql;

CREATE TRIGGER tr_id_synthese_fa
AFTER INSERT ON bdn.faune
    FOR EACH ROW EXECUTE PROCEDURE fill_id_synthese_faune();


CREATE OR REPLACE FUNCTION tr_protocole_to_synthese() RETURNS TRIGGER AS $tr_protocole_to_synthese$
    BEGIN
    INSERT INTO bdn.synthese (id_synthese, protocole, observateur, date, cd_nom, insee, ccod_frt, altitude, valide,geom_point) 
    VALUES( concat_ws('', LEFT(new.protocole,2)::text, new.id_obs::text), new.protocole, new.observateur, new.date, new.cd_nom, new.insee, new.ccod_frt, new.altitude, new.valide, new.geom_point);
    RETURN NEW;
  
    END;
$tr_protocole_to_synthese$ LANGUAGE plpgsql;

CREATE TRIGGER tr_fl_to_synthese
BEFORE INSERT ON bdn.flore
    FOR EACH ROW EXECUTE PROCEDURE tr_protocole_to_synthese();

CREATE TRIGGER tr_fa_to_synthese
BEFORE INSERT ON bdn.faune
    FOR EACH ROW EXECUTE PROCEDURE tr_protocole_to_synthese();


CREATE OR REPLACE VIEW bdn.v_search_taxons AS 
 SELECT DISTINCT s.cd_nom,
    t.nom_vern,
    t.lb_nom,
    s.protocole
   FROM bdn.synthese s
     JOIN taxonomie.taxref t ON s.cd_nom = t.cd_nom;

ALTER TABLE bdn.v_search_taxons
  OWNER TO onfuser;