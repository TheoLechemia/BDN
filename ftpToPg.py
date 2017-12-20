#coding: utf-8

import psycopg2
import psycopg2.extras
import csv
import os
from shutil import copyfile
from datetime import datetime
import traceback
from psycopg2 import sql as psysql

### config ###

PROJECTION = 2545
ID_STRUCTURE = 1
DATABASE_NAME = 'bdn'
DATABASE_USER = 'mon_user_de_dbn'
DATABASE_PASS = 'mon_pass'
DATABASE_HOST = 'mon_ip' #sans le http
DATABASE_PORT = '5432'
FTP_FOLDER = '/home/ubuntu/depot_terrain/Observatory'
FTP_FOLDER_SAVE = '/home/ubuntu/depot_terrain_save'

class DatabaseInterface:
    def __init__(self, conn, cur):
        self.conn = conn
        self.cur = cur

    def closeAll(self):
        self.conn.close()
        self.cur.close()

def getConnexion():
    conn = psycopg2.connect(
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASS,
        host=DATABASE_HOST,
        port=DATABASE_PORT
        )
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    connexion = DatabaseInterface(conn, cur)
    return connexion



def csv2PG(file):
    '''Fonction qui lit chaque ligne d'un fichier CSV pour ajouter l'observation courante dans le BDN '''
    db = getConnexion()
    sql = str()
    generalValues = []

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
            try:
                db.cur.execute(sql, {'input':row['protocole']}) 
                res = db.cur.fetchone()
                id_projet = res[0]
                inputProtocole = res[1]
                fullTableName = inputProtocole+".releve"
            except:
                return traceback.format_exc()

            #recupere les bib champs du protocole de la ligne
            # sql = "SELECT no_spec, nom_champ FROM "+inputProtocole+".bib_champs_"+inputProtocole
            bib_champs_table = "bib_champs_"+inputProtocole
            sql = "SELECT no_spec, nom_champ FROM {sch}.{tbl}"
            sql = psysql.SQL(sql).format(sch=psysql.Identifier(inputProtocole),tbl=psysql.Identifier(bib_champs_table)).as_string(db.cur)
            try:
                db.cur.execute(sql)
                res = db.cur.fetchall()
                fieldList= list()
                for r in res:
                    fieldList.append({'spec_name': r[0], 'field_name': r[1]})
            except:
                return traceback.format_exc()

            observateur = row['observateur_nom']+" "+ row['observateur_prenom']
            protocole = row['protocole']
            comm_loc = row['loc_nom']
            commentaire = row['comment']
            #on enleve l'heure de la date
            date = row['date'].split(' ')[0]
            print 'DATEEEEEEEEEEEE',date
            dateObject = datetime.strptime(date, "%Y-%m-%d")
            lon = row['loc_x']
            lon = lon.replace(',', '.')
            lat = row['loc_y']
            lat = lat.replace(',', '.')
            cd_nom = row['taxon_id']
            #formatage en WKT
            point = 'POINT('+lon+' '+lat+')'
            valide = "FALSE"
            # recuperation du code insee
            sql_insee = " SELECT code_insee FROM layers.commune WHERE ST_INTERSECTS(geom,(ST_Transform(ST_PointFromText(%s, 4326),"+str(config['MAP']['PROJECTION'])+")))"
            param = [point]
            try:
                db.cur.execute(sql_insee, param)
                resinsee = db.cur.fetchone()
                insee = None
                if resinsee != None:
                    insee = resinsee[0]
            except:
                return traceback.format_exc()

            #recuperation du code foret
            sql_foret = " SELECT ccod_frt FROM layers.perimetre_forets WHERE ST_INTERSECTS(geom,(ST_Transform(ST_PointFromText(%s, 4326),"+str(config['MAP']['PROJECTION'])+"))) "
            try:
                db.cur.execute(sql_foret, param)
                ccod_frt = None 
                res = db.cur.fetchone()
                if res != None:
                    ccod_frt = res[0]
            except:
                return traceback.format_exc()

            id_structure = ID_STRUCTURE
            loc_exact = True
            code_maille = None

            stringInsert = "INSERT INTO "+fullTableName+"(id_projet, observateur, date, cd_nom, geom_point, insee, commentaire, valide, ccod_frt, loc_exact, code_maille, id_structure, comm_loc, diffusable"
            stringValues = " VALUES (%s, %s, %s, %s,  ST_Transform(ST_PointFromText(%s, 4326),"+str(config['MAP']['PROJECTION'])+"), %s, %s, %s, %s, %s, %s, %s, %s, %s"

            generalValues = [id_projet, observateur, dateObject, cd_nom, point, insee, commentaire, valide, ccod_frt, loc_exact, code_maille, id_structure, comm_loc, True]
            try:
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
            except:
                return traceback.format_exc()

            stringInsert+=")"
            stringValues+=");"

            sql = stringInsert+stringValues
            try:
                db.cur.execute(sql, generalValues)
            except:
                return traceback.format_exc()

    db.conn.commit()
    db.closeAll()
    return u'Fichier importé avec succès'


def ftp_to_pg():
    for path,dirs,files in os.walk(FTP_FOLDER):
        for filename in files:
            file_path = os.path.join(path,filename)
            print file_path
            #try to write in PG and copy the csv_file in the save folder
            try:
                csv2PG(file_path)
                copyfile(file_path, FTP_FOLDER_SAVE+'/'+filename)
            except:
                print 'error with ' + file_path
            # if copy success, remove from ftp folder
            else:
                os.remove(file_path)


if __name__ == '__main__':
    ftp_to_pg()
