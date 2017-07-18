--POINT
INSERT INTO synthese.releve (id_lot, id_projet, id_sous_projet, id_sous_projet_2, geom_point, cd_nom, precision, observateur, date, nombre, loc_exact, insee, ccod_frt, valide, diffusable, id_structure)
SELECT i.id_obs,i.id_projet, i.id_sous_projet, i.id_sous_projet_2, ST_SETSRID(ST_GeomFromText(CONCAT('POINT (',i.x,' ',i.y, ')')),32620), i.cd_ref, i.precision, i.observateur,i.date, i.nombre, TRUE, c.code_insee, f.ccod_frt, TRUE, TRUE, 2
FROM import i
LEFT JOIN layers.commune c ON ST_INTERSECTS(ST_SETSRID(ST_GeomFromText(CONCAT('POINT (',i.x,' ',i.y, ')')),32620), c.geom)
LEFT JOIN layers.perimetre_forets f ON ST_INTERSECTS(ST_SETSRID(ST_GeomFromText(CONCAT('POINT (',i.x,' ',i.y, ')')),32620), f.geom)

-- MAILLE
WITH code_maille_j AS(
SELECT id_maille, unique_id
FROM import i
JOIN layers.maille_1_2 l ON ST_INTERSECTS(ST_SETSRID(ST_GeomFromText(CONCAT('POINT (',i.x,' ',i.y, ')')),32620),l.geom )
WHERE l.taille_maille = '2'
)
INSERT INTO synthese.releve (id_lot, id_projet, id_sous_projet, id_sous_projet_2, cd_nom, code_maille, precision, observateur, date, nombre, loc_exact, insee, ccod_frt, valide, diffusable, id_structure)
SELECT i.id_obs,i.id_projet, i.id_sous_projet, i.id_sous_projet_2,  i.cd_ref, j.id_maille, i.precision, i.observateur,i.date, i.nombre, FALSE, c.code_insee, f.ccod_frt, TRUE, TRUE, 2
FROM import i
LEFT JOIN layers.commune c ON ST_INTERSECTS(ST_SETSRID(ST_GeomFromText(CONCAT('POINT (',i.x,' ',i.y, ')')),32620), c.geom)
LEFT JOIN layers.perimetre_forets f ON ST_INTERSECTS(ST_SETSRID(ST_GeomFromText(CONCAT('POINT (',i.x,' ',i.y, ')')),32620), f.geom)
JOIN code_maille_j j ON j.unique_id = i.unique_id



-- import foret humide
INSERT INTO pp_foret_humide.releve (id_releve, id_projet, id_sous_projet, id_sous_projet_2, geom_point, cd_nom, precision, observateur, date, loc_exact, insee, ccod_frt, valide, diffusable, id_structure, placeau, no_arbre, x_placeau, y_placeau, x_placette, y_placette )
SELECT i.id_obs,i.id_projet, i.id_sous_projet, i.id_sous_projet_2, ST_SETSRID(ST_GeomFromText(CONCAT('POINT (',i.x,' ',i.y, ')')),32620), i.cd_ref, i.precision, i.observateur,i.date, TRUE, c.code_insee, f.ccod_frt, TRUE, TRUE, 2, placeau, i.no_arbre, i.x_placeau, i.y_placeau, i.x_placette, i.y_placette
FROM import_pp_foret_humide i
LEFT JOIN layers.commune c ON ST_INTERSECTS(ST_SETSRID(ST_GeomFromText(CONCAT('POINT (',i.x,' ',i.y, ')')),32620), c.geom)
LEFT JOIN layers.perimetre_forets f ON ST_INTERSECTS(ST_SETSRID(ST_GeomFromText(CONCAT('POINT (',i.x,' ',i.y, ')')),32620), f.geom)

-- import enclos_reg
INSERT INTO enclos_rg_fl.releve (id_releve, id_projet, id_sous_projet, id_sous_projet_2, geom_point, cd_nom, precision, observateur, date, loc_exact, insee, ccod_frt, valide, diffusable, id_structure, strate, nom_taxon_orig )
SELECT i.id_obs,i.id_projet, i.id_sous_projet, i.id_sous_projet_2, ST_SETSRID(ST_GeomFromText(CONCAT('POINT (',i.x,' ',i.y, ')')),32620), i.cd_ref, i.precision, i.observateur,i.date, TRUE, c.code_insee, f.ccod_frt, TRUE, TRUE, 2, i.strate, i.nom_taxon_orig
FROM import_enclos_reg i
LEFT JOIN layers.commune c ON ST_INTERSECTS(ST_SETSRID(ST_GeomFromText(CONCAT('POINT (',i.x,' ',i.y, ')')),32620), c.geom)
LEFT JOIN layers.perimetre_forets f ON ST_INTERSECTS(ST_SETSRID(ST_GeomFromText(CONCAT('POINT (',i.x,' ',i.y, ')')),32620), f.geom)

-- import p_eee_cd
INSERT INTO parcelle_lutte_eee_marche_cd.releve (id_releve, id_projet, id_sous_projet, id_sous_projet_2, geom_point, cd_nom, precision, observateur, date, loc_exact, insee, ccod_frt, valide, diffusable, id_structure,site, parcelle, "A_inf_10cm", "B_10cm_1m", "C_1m_10cm", "D_sup_10cm", type_bio, plante)
SELECT i.id_releve, i.id_projet, i.id_sous_projet, i.id_sous_projet_2, ST_SETSRID(ST_GeomFromText(CONCAT('POINT (',i.x,' ',i.y, ')')),32620), i.cd_ref, i.precision, i.observateur,i.date, TRUE, c.code_insee, f.ccod_frt, TRUE, TRUE, 2, i.site, i.parcelle, i."A_inf_10cm", i."B_10cm_1m", i."C_1m_10cm", i."D_sup_10cm", i.type_bio, i.plante
FROM parcelle_eee_cd i
LEFT JOIN layers.commune c ON ST_INTERSECTS(ST_SETSRID(ST_GeomFromText(CONCAT('POINT (',i.x,' ',i.y, ')')),32620), c.geom)
LEFT JOIN layers.perimetre_forets f ON ST_INTERSECTS(ST_SETSRID(ST_GeomFromText(CONCAT('POINT (',i.x,' ',i.y, ')')),32620), f.geom)


-- import pp foret_seche

INSERT INTO pp_foret_seche.releve (id_releve, id_projet, id_sous_projet, id_sous_projet_2, geom_point, cd_nom, precision, observateur, date, loc_exact, insee, ccod_frt, valide, diffusable, id_structure, placeau, no_tige, circ, surface, "C_10_15", "C_15_20", "C_20_25", "C_25_30", "C_30_35", "C_35_40", "C_40_45", "C_45_50", "C_50_plus", "Souche", redondance_souche, "Observations", probleme)
SELECT i.id_releve, i.id_projet, i.id_sous_projet, i.id_sous_projet_2, ST_SETSRID(ST_GeomFromText(CONCAT('POINT (',i.x,' ',i.y, ')')),32620), i.cd_ref, i.precision, i.observateur,i.date, TRUE, c.code_insee, f.ccod_frt, TRUE, TRUE, 2, i.placeau, i.no_tige, i.circ, i.surface, i."C_10_15", i."C_15_20", i."C_20_25", i."C_25_30", i."C_30_35", i."C_35_40", i."C_40_45", i."C_45_50", i."C_50_plus", i."Souche", i.redondance_souche, i."Observations", i.probleme
FROM pp_foret_seche i
LEFT JOIN layers.commune c ON ST_INTERSECTS(ST_SETSRID(ST_GeomFromText(CONCAT('POINT (',i.x,' ',i.y, ')')),32620), c.geom)
LEFT JOIN layers.perimetre_forets f ON ST_INTERSECTS(ST_SETSRID(ST_GeomFromText(CONCAT('POINT (',i.x,' ',i.y, ')')),32620), f.geom)
