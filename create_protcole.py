# coding: utf-8
import csv
import sys
from Apps.config import config, database
from Apps.database import *


fileName = input('Entrez le chemin du fichier CSV (entre guillemets) : ')





#try:

inter = fileName.split('.')
schemaName = inter[0].split('\\')[-1]
fullName = schemaName+".releve"

db = getConnexion()
sql = " CREATE SCHEMA "+ schemaName+" AUTHORIZATION "+ database['USER']
db.cur.execute(sql)
db.conn.commit()


column_name_and_type = list()
with open(fileName) as csvfile:
    reader = csv.reader(csvfile, delimiter = ';', quotechar= '"')
    next(reader, None)

    #create table
    for row in reader:
        column_name_and_type.append({'name':row[0], 'htmlType' : row[1], 'db_type': row[2]})


stringCreate = """CREATE TABLE """+fullName+""" 
(
  id_obs serial CONSTRAINT """+schemaName+"""_PK PRIMARY KEY,
  id_synthese integer,
  observateur character varying(100) NOT NULL,
  date date NOT NULL,
  cd_nom integer NOT NULL,
  geom_point geometry(Point,"""+str(config['MAP']['PROJECTION'])+"""),
  insee character varying(10),
  altitude integer,
  commentaire character varying(150),
  comm_loc character varying(150),
  valide boolean,
  ccod_frt character varying(50),
  loc_exact boolean,
  code_maille character varying(20),
  id_structure integer,"""

addPermission = "ALTER TABLE "+fullName+" OWNER TO "+database['USER']+";"
for r in column_name_and_type:
    stringCreate+=" "+ r['name']+" "+r['db_type']+","

stringCreate = stringCreate[0:-1]+");"
stringCreate += addPermission

db.cur.execute(stringCreate)
db.conn.commit()


# ##Cree la vue pour y mettre la liste des taxons personnalisé. Par default on met tous le taxref, a change par le gestionnaire de BDD

sql = "CREATE VIEW taxonomie.taxons_"+schemaName+" AS SELECT * FROM taxonomie.taxref;"
sql += "ALTER TABLE taxonomie.taxons_"+schemaName+" OWNER TO "+database['USER']+";"
db.cur.execute(sql)
db.conn.commit()

# #create trigers

trigger = """CREATE TRIGGER tr_"""+schemaName+"""_to_synthese
            AFTER INSERT ON """+fullName+"""
            FOR EACH ROW EXECUTE PROCEDURE synthese.tr_protocole_to_synthese();"""

db.cur.execute(trigger)
db.conn.commit()





stringCreate = "CREATE TABLE "+schemaName+".bib_champs_"+schemaName+" ( id serial NOT NULL, id_champ integer, no_spec character varying, nom_champ character varying, valeur character varying, CONSTRAINT "+schemaName+"bib_champs_PK PRIMARY KEY (id));"
stringCreate += " ALTER TABLE "+schemaName+".bib_champs_"+schemaName+" OWNER TO "+database['USER']+";"
db.cur.execute(stringCreate)
db.conn.commit()


sql = "INSERT INTO synthese.bib_protocole VALUES ('"+schemaName.title()+"', '"+schemaName+"' , 'releve', '"+fullName+"', 'addObs/"+schemaName+".html', '"+schemaName+".bib_champs_"+schemaName+"')"
db.cur.execute(sql)
db.conn.commit()


with open(fileName) as csvfile:
    reader = csv.reader(csvfile, delimiter = ';', quotechar= '"')
    next(reader, None)

    #fill table bib_champ
    spec_number = 1
    for row in reader:
        #table_row = row[0].split(',')
        column_name = row[0]
        i=3
        field_number = 1
        string_spec_number = str()
        if row[1] == 'Liste de choix':
            liste_deroulante_tab = list()
            while i<len(row) and row[i]!= '':
                value = row[i]
                sql = "INSERT INTO "+schemaName+".bib_champs_"+schemaName+"(id_champ, no_spec, nom_champ, valeur) VALUES(%s, %s, %s, %s) "
                string_spec_number = 'spec_'+str(spec_number)
                value = value.decode('utf-8')
                params = [field_number, string_spec_number , column_name, value]
                print params
                db.cur.execute(sql, params)
                db.conn.commit()
                i += 1
                field_number += 1
        else:
            sql = "INSERT INTO "+schemaName+".bib_champs_"+schemaName+"(id_champ, no_spec, nom_champ, valeur) VALUES(%s, %s, %s, %s) "
            string_spec_number = 'spec_'+str(spec_number)  
            params = [None, string_spec_number , column_name, None]
            db.cur.execute(sql, params)
            db.conn.commit()      	
        spec_number += 1


#vue pour les export en shapefile

string_create_view_poly = """CREATE OR REPLACE VIEW """+schemaName+""".layer_poly AS 
 SELECT t.nom_vern,
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
    f.id_synthese,"""
for r in column_name_and_type:
  string_create_view_poly += "f."+r['name']+' ,'
string_create_view_poly = string_create_view_poly[:-1]

string_create_view_poly += """ FROM """+schemaName+""".releve f
    JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
    JOIN layers.mailles_1k m ON m.code_1km::text = f.code_maille::text
    JOIN utilisateur.bib_structure s ON f.id_structure = s.id_structure
     WHERE f.valide = TRUE AND f.loc_exact = FALSE;"""

string_create_view_point = """CREATE OR REPLACE VIEW """+schemaName+""".layer_point AS 
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
    f.id_synthese,"""
for r in column_name_and_type:
  string_create_view_point += "f."+r['name']+' ,'
string_create_view_point = string_create_view_point[:-1]

string_create_view_point += """ FROM """+schemaName+""".releve f
   JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
   JOIN layers.mailles_1k m ON m.code_1km::text = f.code_maille::text 
   JOIN utilisateur.bib_structure s ON f.id_structure = s.id_structure
   WHERE f.valide=true AND loc_exact = false; """

db.cur.execute(string_create_view_poly)
db.cur.execute(string_create_view_point)
db.conn.commit()  


string_create_view_point += " ALTER VIEW "+schemaName+".layer_point OWNER TO "+database['USER']+";"
string_create_view_poly += " ALTER VIEW "+schemaName+".layer_poly OWNER TO "+database['USER']+";"

db.cur.execute(string_create_view_poly)
db.cur.execute(string_create_view_point)
db.conn.commit()  





htmlFileName = ".\\Apps\\addObs\\static\\"+schemaName+".html"
htmlFile = open(htmlFileName, "w")

htmlContent = """<div class='form-group'> 
            """

integerInput = "<input class='form-control' type='number' placeholder='{}' ng-model='child.protocoleForm.{}'  name='{}'> \n"
simpleTextInput = "<input class='form-control' type='text' placeholder='{}' ng-model='child.protocoleForm.{}'  name='{}'> \n"
booleanInput = """<div'> 
                    <select class='form-control' type='text' placeholder='{}' ng-model='child.protocoleForm.{}'  > \n
                      <option value=""> -{}- </option> 
                      <option value="True">  Oui  </option> \n
                      <option value="False">  Non  </option> \n
                    </select>\n
                  </div> \n"""
listInput = "<div> <select class='form-control' type='text' placeholder='{}' ng-model='child.protocoleForm.{}' ng-options='choice as choice for choice in fields.{}' > <option value=""> - {} - </option> </select>  </div> \n"

for r in column_name_and_type:
    print r['htmlType']
    if r['htmlType'] == 'Entier' or r['htmlType'] == 'Reel' :
        write  =  integerInput.format(r['name'],r['name'],r['name'])
        htmlFile.write(write)
    if r['htmlType'] == 'Chaîne de caractère':
        write  =  simpleTextInput.format(r['name'],r['name'],r['name'])
        htmlFile.write(write)
    if r['htmlType'] == 'Booléen':
        write  =  booleanInput.format(r['name'],r['name'], r['name'])
        htmlFile.write(write)
    if r['htmlType'] == "Liste de choix" :
        write = listInput.format(r['name'],r['name'],r['name'], r['name'])
        htmlFile.write(write)
htmlFile.close()

print "PROTCOLE AJOUTE AVEC SUCCES"

db.closeAll()

#except:
    # e = sys.exc_info()[0]
    # print "Une erreur s'est produite: "
    # print e

