#coding: utf-8
import psycopg2
import csv
from datetime import datetime
from flask import session
from Apps.database import *
from ..config import config

# def getSpec(specNumber, row, interpretationDict):
#     stringList = row[specNumber].split('#')
#     print stringList
#     value = None
#     #si le champs n'est pas vide on recupere l'id situe apres le #
#     if len(stringList) != 1:
#         specInt = int(stringList[1])
#         try:
#             value = interpretationDict[specNumber][specInt]
#             #if value = '': ce n'est pas un champs a choix mutliple, on recupere juste le nombre rentre avec le #
#         except KeyError:
#             print "Une erreur est survenue, vérifier le tableau de conversion des champs generiques"
#             value = stringList[1]
#     print value
#     return value

# def getSpec_without_dict(specNumber, row):
#     tabInter = row[specNumber].split('#')
#     value = None
#     if len(tabInter) != 1:
#         value = tabInter[1]
#     return value

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

        for row in reader:
            ###COMMUN###
            #recupere les infos sur le projet de la ligne
            sql = """SELECT id_projet, nom_schema from synthese.bib_projet
					WHERE nom_projet = %(input)s OR nom_schema = %(input)s """
            db.cur.execute(sql, {'input':row['protocole']}) 
            res = db.cur.fetchone()
            id_projet = res[0]
            inputProtocole = res[1]
            fullTableName = inputProtocole+".releve"

            #recupere les bib champs du protocole de la ligne
            sql = "SELECT no_spec, nom_champ FROM "+inputProtocole+".bib_champs_"+inputProtocole
            db.cur.execute(sql)
            res = db.cur.fetchall()
            fieldList= list()
            for r in res:
                fieldList.append({'spec_name': r[0], 'field_name': r[1]})

            observateur = row['observateur_nom']+" "+ row['observateur_prenom']
            protocole = row['protocole']
            comm_loc = row['loc_nom']
            commentaire = row['comment']
            #on enleve l'heure de la date
            listDate = row['date'].split(' ')
            date = listDate[0]
            dateObject = datetime.strptime(date, "%Y-%M-%d")
            lon = row['loc_x']
            lon = lon.replace(',', '.')
            lat = row['loc_y']
            lat = lat.replace(',', '.')
            cd_nom = row['taxon_id']
            #formatage en WKT
            point = 'POINT('+lon+' '+lat+')'
            valide = "FALSE"
            sql_insee = " SELECT code_insee FROM layers.commune WHERE ST_INTERSECTS(geom,(ST_Transform(ST_PointFromText(%s, 4326),"+str(config['MAP']['PROJECTION'])+")))"
            param = [point]
            db.cur.execute(sql_insee, param)
            resinsee = db.cur.fetchone()
            insee = None
            if resinsee != None:
                insee = resinsee[0]

            sql_foret = " SELECT ccod_frt FROM layers.perimetre_forets WHERE ST_INTERSECTS(geom,(ST_Transform(ST_PointFromText(%s, 4326),"+str(config['MAP']['PROJECTION'])+"))) "
            db.cur.execute(sql_foret, param)
            ccod_frt = None 
            res = db.cur.fetchone()
            if res != None:
                ccod_frt = res[0]

            #recupere l'id_structure depuis la session
            id_structure = session['id_structure']
            loc_exact = True
            code_maille = None

            stringInsert = "INSERT INTO "+fullTableName+"(id_projet, observateur, date, cd_nom, geom_point, insee, commentaire, valide, ccod_frt, loc_exact, code_maille, id_structure, comm_loc, diffusable"
            stringValues = " VALUES (%s, %s, %s, %s,  ST_Transform(ST_PointFromText(%s, 4326),"+str(config['MAP']['PROJECTION'])+"), %s, %s, %s, %s, %s, %s, %s, %s, %s"

            generalValues = [id_projet, observateur, date, cd_nom, point, insee, commentaire, valide, ccod_frt, loc_exact, code_maille, id_structure, comm_loc, True]
            for field in fieldList:

                tabInter = row[field['spec_name']].split('#')
                value = None
                if len(tabInter) != 1:
                    value = tabInter[1]
                stringInsert += ", "+field['field_name']
                stringValues += ", %s"
                if value != None:
                    value = value.capitalize()
                generalValues.append(value)

            stringInsert+=")"
            stringValues+=");"

            sql = stringInsert+stringValues
            db.cur.execute(sql, generalValues)
            db.conn.commit()

    db.cur.close()
    db.closeAll()

