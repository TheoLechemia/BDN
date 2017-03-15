# coding: utf-8
import csv
import sys
from Apps import config
from Apps.database import *

fileName = input('Entrez le chemin du fichier CSV (entre guillemets) : ')





try:

	inter = fileName.split('.')
	schemaName = inter[0].split('\\')[-1]
	fullName = schemaName+".releve"

	db = getConnexion()
	sql = " CREATE SCHEMA "+ schemaName+" AUTHORIZATION "+ config.USER
	db.cur.execute(sql)
	db.conn.commit()


	column_name_and_type = list()
	with open(fileName) as csvfile:
	    reader = csv.reader(csvfile, delimiter = ';', quotechar= '"')
	    next(reader, None)

	    #create table
	    for row in reader:
	        column_name_and_type.append({'name':row[0], 'type': row[2]})



	stringCreate = """CREATE TABLE """+fullName+""" 
	(
	  id_obs serial CONSTRAINT """+schemaName+"""_PK PRIMARY KEY,
	  id_synthese character varying(15),
	  observateur character varying(100) NOT NULL,
	  date date NOT NULL,
	  cd_nom integer NOT NULL,
	  geom_point geometry(Point,"""+str(config.PROJECTION)+"""),
	  insee character varying(10),
	  altitude integer,
	  commentaire character varying(150),
	  valide boolean,
	  ccod_frt character varying(50),
	  loc_exact boolean,
	  code_maille character varying(20),
	  id_structure integer,"""

	addPermission = "ALTER TABLE "+fullName+" OWNER TO "+config.USER+";"
	for r in column_name_and_type:
	    stringCreate+=" "+ r['name']+" "+r['type']+","

	stringCreate = stringCreate[0:-1]+");"
	stringCreate += addPermission

	db.cur.execute(stringCreate)
	db.conn.commit()


	# ##Cree la vue pour y mettre la liste des taxons personnalisé. Par default on met tous le taxref, a change par le gestionnaire de BDD

	sql = "CREATE VIEW taxonomie.taxons_"+schemaName+" AS SELECT * FROM taxonomie.taxref;"
	sql += "ALTER TABLE taxonomie.taxons_"+schemaName+" OWNER TO "+config.USER+";"
	db.cur.execute(sql)
	db.conn.commit()

	# #create trigers

	trigger = """CREATE TRIGGER tr_"""+schemaName+"""_to_synthese
	            AFTER INSERT ON """+fullName+"""
	            FOR EACH ROW EXECUTE PROCEDURE synthese.tr_protocole_to_synthese();"""

	db.cur.execute(trigger)
	db.conn.commit()





	stringCreate = "CREATE TABLE "+schemaName+".bib_champs_"+schemaName+" ( id serial NOT NULL, nom_champ character varying, valeur character varying, CONSTRAINT "+schemaName+"bib_champs_PK PRIMARY KEY (id));"
	stringCreate += " ALTER TABLE "+schemaName+".bib_champs_"+schemaName+" OWNER TO "+config.USER+";"
	db.cur.execute(stringCreate)
	db.conn.commit()


	sql = "INSERT INTO synthese.bib_protocole VALUES ('"+schemaName.title()+"', '"+schemaName+"' , 'releve', '"+fullName+"', 'addObs/"+schemaName+".html', '"+schemaName+".bib_champs_"+schemaName+"')"
	db.cur.execute(sql)
	db.conn.commit()


	with open(fileName) as csvfile:
	    reader = csv.reader(csvfile, delimiter = ';', quotechar= '"')
	    next(reader, None)

	    #create table
	    for row in reader:
	        #table_row = row[0].split(',')
	        column_name = row[0]
	        i=3
	        if row[1] == 'liste_deroulante':
	            liste_deroulante_tab = list()
	            while i<len(row) and row[i]!= '':
	                value = row[i]
	                sql = "INSERT INTO "+schemaName+".bib_champs_"+schemaName+"(nom_champ, valeur) VALUES(%s, %s) "
	                params = [column_name, value]
	                db.cur.execute(sql, params)
	                db.conn.commit()
	                i += 1

	db.closeAll()

	htmlFileName = ".\\Apps\\addObs\\static\\"+schemaName+".html"
	htmlFile = open(htmlFileName, "w")

	htmlContent = """<div class='form-group'> 
	            """

	integerInput = "<input class='form-control' type='number' placeholder='{}' ng-model='child.protocoleForm.{}'  name='{}'> \n"
	listInput = "<div'> <select class='form-control' type='text' placeholder='{}' ng-model='child.protocoleForm.{}' ng-options='choice as choice for choice in fields.{}' > <option value=""> - {} - </option> </select>  </div> \n"

	for r in column_name_and_type:
	    if r['type'] == 'integer':
	        write  =  integerInput.format(r['name'],r['name'],r['name'])
	        htmlFile.write(write)
	    else:
	        write = listInput.format(r['name'],r['name'],r['name'], r['name'])
	        htmlFile.write(write)
	htmlFile.close()

	print "PROTCOLE AJOUTE AVEC SUCCES"

except:
    e = sys.exc_info()[0]
    print "Une erreur s'est produite: "
    print e

