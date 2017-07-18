CREATE FOREIGN TABLE utilisateurs.bib_organismes
   (  nom_organisme character varying(100) NOT NULL,
  adresse_organisme character varying(128),
  cp_organisme character varying(5),
  ville_organisme character varying(100),
  tel_organisme character varying(14),
  fax_organisme character varying(14),
  email_organisme character varying(100),
  id_organisme integer NOT NULL
   )
   SERVER server_usershubdb;
ALTER FOREIGN TABLE utilisateurs.bib_organismes
  OWNER TO onf_admin;



CREATE FOREIGN TABLE utilisateurs.t_applications
   (id_application integer ,
    nom_application character varying(50) NOT NULL,
    desc_application text )
   SERVER server_usershubdb;
ALTER FOREIGN TABLE utilisateurs.t_applications
  OWNER TO onf_admin;


CREATE FOREIGN TABLE utilisateurs.t_roles
   (groupe boolean NOT NULL,
    id_role integer ,
    identifiant character varying(100) ,
    nom_role character varying(50) ,
    prenom_role character varying(50) ,
    desc_role text ,
    pass character varying(100) ,
    email character varying(250) ,
    id_organisme integer ,
    organisme character(32) ,
    id_unite integer ,
    remarques text ,
    pn boolean ,
    session_appli character varying(50) ,
    date_insert timestamp without time zone ,
    date_update timestamp without time zone )
   SERVER server_usershubdb;
ALTER FOREIGN TABLE utilisateurs.t_roles
  OWNER TO onf_admin;



CREATE FOREIGN TABLE utilisateurs.v_userslist_forall_applications
   (groupe boolean ,
    id_role integer ,
    identifiant character varying(100) ,
    nom_role character varying(50) ,
    prenom_role character varying(50) ,
    desc_role text ,
    pass character varying(100) ,
    email character varying(250) ,
    id_organisme integer ,
    organisme character varying(32) ,
    id_unite integer ,
    remarques text ,
    pn boolean ,
    session_appli character varying(50) ,
    date_insert timestamp without time zone ,
    date_update timestamp without time zone ,
    id_droit_max integer ,
    id_application integer )
   SERVER server_usershubdb;
ALTER FOREIGN TABLE utilisateurs.v_userslist_forall_applications
  OWNER TO onf_admin;
