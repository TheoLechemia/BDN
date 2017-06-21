#coding: utf-8
import psycopg2
import csv
from datetime import datetime
from flask import session
from Apps.database import *
from ..config import config
import traceback

def csv2PG(file):
    db = getConnexion()
    sql = str()
    generalValues = []

    # try: 
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter = ';', quotechar= '|')
        inputProtocole = None
        fieldList = None
        fullTableName = str()
        interpretationDict = None

        no_ligne = 0
        for row in reader:
            ###COMMUN###
            #recupere les infos sur le projet de la ligne
            sql = """SELECT id_projet, nom_schema from synthese.bib_projet
					WHERE id_projet = %(input)s """
            id_projet = None
            inputProtocole = None
            fullTableName = None
            try:
                db.cur.execute(sql, {'input':int(row['ID_projet'])})
                res = db.cur.fetchone()
                id_projet = res[0]
                inputProtocole = res[1]
                fullTableName = inputProtocole+".releve"
            except:
                return "L'id_projet de la ligne "+str(no_ligne)+" est incorect"


            #recupere les bib champs du protocole de la ligne, si ils existe - si donnee simple la table n'existe pas
            if inputProtocole != "synthese":
                sql = "SELECT nom_champ FROM "+inputProtocole+".bib_champs_"+inputProtocole
                fieldList= list()
                try:
                    db.cur.execute(sql)
                    res = db.cur.fetchall()
                    for r in res:
                        fieldList.append(r[0])
                except:
                    print "il n'y a pas d table bib_champ"

            try:
                #recupere les champs communs
                id_sous_projet = row['ID_sous_projet']
                id_sous_projet_2 = row['ID_sous_projet_2']
                observateur = row['Observateur']
                lon = row['x']
                lat = row['y']
                cd_ref = row['CD_REF']
                precision = row['Precision']
                commentaire_loc = row['Commentaire_loc']
                isMaille = row['Maille']
                taille_maille = row['Taille_maille']
                observateur = row['Observateur']
                date = row['Date']
                dateObject = datetime.strptime(date, "%d/%M/%Y")
                diffusable = row['Diffusable']
                id_structure = row['ID_structure']
                commentaire = row['Commentaire']
            except:
                return "Le nom d'une colonne du CSV est incorect, se réferer au modele \n "+traceback.format_exc()

            #recuperation des infos dans les tables geometriques - schema layers
            #formatage en WKT
            point = 'POINT('+lon+' '+lat+')'
            valide = "FALSE"
            sql_insee = " SELECT code_insee FROM layers.commune WHERE ST_INTERSECTS(geom,(ST_Transform(ST_PointFromText(%s, 32620),"+str(config['MAP']['PROJECTION'])+")))"
            param = [point]
            insee = None
            db.cur.execute(sql_insee, [point])
            resinsee = db.cur.fetchone()
            if resinsee != None:
                insee = resinsee[0]
            #except:
                #return traceback.format_exc()

            sql_foret = " SELECT ccod_frt FROM layers.perimetre_forets WHERE ST_INTERSECTS(geom,(ST_Transform(ST_PointFromText(%s, 32620),"+str(config['MAP']['PROJECTION'])+")))"
            ccod_frt = None 
            try:
                db.cur.execute(sql_foret, param)
                resForet = db.cur.fetchone()
                if resForet != None:
                    ccod_frt = resForet[0]
            except:
                return traceback.format_exc()
            if isMaille in ['TRUE', 'True', 'T', 't', 'Oui', 'oui', 'o']:
                ##rechercher le code maille
                sql_maille = "SELECT id_maille FROM layers.maille_1_2 WHERE ST_INTERSECTS(geom,(ST_Transform(ST_PointFromText(%s, 32620),"+str(config['MAP']['PROJECTION'])+"))) AND taille_maille = %s"
                code_maille = None
                try:
                    param = [point, taille_maille]
                    db.cur.execute(sql_maille, param)
                    resMaille = db.cur.fetchone()
                    if resMaille != None:
                        code_maille = resMaille[0]
                except:
                    return traceback.format_exc()

                stringInsert = "INSERT INTO "+fullTableName+"(id_projet, id_sous_projet, id_sous_projet_2, code_maille, cd_nom, precision, comm_loc, observateur, date, diffusable, id_structure, commentaire, insee, ccod_frt, valide, loc_exact "
                stringValues = " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
                generalValues = [id_projet, id_sous_projet, id_sous_projet_2, code_maille, cd_ref, precision, commentaire_loc, observateur, date, diffusable, id_structure, commentaire, insee, ccod_frt , True, isMaille]
            #Ce n'est pas une maille
            else:
                stringInsert = "INSERT INTO "+fullTableName+"(id_projet, id_sous_projet, id_sous_projet_2, geom_point, cd_nom, precision, comm_loc, observateur,date, diffusable, id_structure, commentaire, insee, ccod_frt, valide, loc_exact "
                stringValues = " VALUES (%s, %s, %s, ST_Transform(ST_PointFromText(%s, "+str(config['MAP']['PROJECTION'])+"),"+str(config['MAP']['PROJECTION'])+"), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
                generalValues = [id_projet, id_sous_projet, id_sous_projet_2, point, cd_ref, precision, commentaire_loc, observateur, date, diffusable, id_structure, commentaire, insee, ccod_frt, True, not isMaille]
            if fieldList != None:
                for field in fieldList:
                    stringInsert += ', '+field
                    stringValues += ", %s"
                    generalValues.append(row[field])

            stringInsert+=")"
            stringValues+=");"

            sql = stringInsert+stringValues
            try:
                print db.cur.mogrify(sql, generalValues)
                db.cur.execute(sql, generalValues)
            except:
                return " Une erreur s'est produite à la ligne : "+ str(no_ligne)+ " du fichier CSV: \n   "+traceback.format_exc()

            #incremente le numero de la ligne pour garder la trace
            no_ligne = no_ligne + 1
    db.conn.commit()
    db.cur.close()
    db.closeAll()

    return u'Fichier importé avec succès'