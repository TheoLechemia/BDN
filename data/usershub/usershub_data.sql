DELETE FROM utilisateurs.t_roles;
DELETE FROM utilisateurs.cor_role_droit_application;
DELETE FROM utilisateurs.bib_organismes;


INSERT INTO utilisateurs.bib_organismes (nom_organisme, id_organisme) VALUES ('ONF', 2), ('Réserves', 3), ('Autre', 4);

INSERT INTO utilisateurs.t_roles  (groupe, id_role, identifiant, nom_role, pass, id_unite,id_organisme, organisme, pn) VALUES (FALSE, 1, 'admin', 'administrateur', '21232f297a57a5a743894a0e4a801fc3',99, 2, 'ONF', TRUE);


INSERT INTO utilisateurs.t_applications VALUES (3, 'BDN', 'Application BDN: gestion des données naturalistes');
INSERT INTO utilisateurs.cor_role_droit_application VALUES (1, 6, 3);
INSERT INTO utilisateurs.cor_role_droit_application VALUES (1, 6, 2);

UPDATE utilisateurs.bib_droits
SET nom_droit = 'lecteur' WHERE id_droit = 1;
UPDATE utilisateurs.bib_droits
SET nom_droit = 'contributeur' WHERE id_droit = 2;
UPDATE utilisateurs.bib_droits
SET nom_droit = 'validateur' WHERE id_droit = 3;
UPDATE utilisateurs.bib_droits 
SET nom_droit = ' administrateur' WHERE id_droit = 6;

DELETE FROM utilisateurs.bib_droits WHERE id_droit IN (4,5);