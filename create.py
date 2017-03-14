# coding: utf-8
import csv
import sys
from Apps import config
from Apps.database import *

fileName = input('Entrez le chemin du fichier CSV (entre guillemets) : ')

print type(fileName)

try:
    db = getConnexion()

    inter = fileName.split('.')
    print inter
    tableName = inter[0].split('\\')[-1]
    print tableName

    column_name_and_type = list()
    with open("C:\\Users\\tl90744\\Documents\\BDN\\tortues.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter = ';', quotechar= '"')
        next(reader, None)

        #create table
        for row in reader:
            column_name_and_type.append({'name':row[0], 'type': row[2]})


    addPermission = "ALTER TABLE bdn."+tableName+" OWNER TO "config.USER";"
    stringCreate = """CREATE TABLE bdn."""+tableName+"""
    (
      id_obs serial CONSTRAINT """+tableName+"""_PK PRIMARY KEY,
      id_synthese character varying(15),
      protocole character varying(50) NOT NULL,
      observateur character varying(100) NOT NULL,
      date date NOT NULL,
      cd_nom integer NOT NULL,
      geom_point geometry(Point,"""+config.PROJECTONN"""),
      insee character varying(10),
      altitude integer,
      commentaire character varying(150),
      valide boolean,
      ccod_frt character varying(50),
      loc_exact boolean,
      code_maille character varying(20),
      id_structure integer,"""

    for r in column_name_and_type:
        stringCreate+=" "+ r['name']+" "+r['type']+","

    stringCreate = stringCreate[0:-1]+");"
    stringCreate += addPermission

    db.cur.execute(stringCreate)
    db.conn.commit()


    # ##Cree la vue pour y mettre la liste des taxons personnalisé. Par default on met tous le taxref, a change par le gestionnaire de BDD

    sql = "CREATE VIEW taxonomie.taxons_"+tableName+" AS SELECT * FROM taxonomie.taxref;"
    sql += addPermission
    db.cur.execute(sql)
    db.conn.commit()

    # #create trigers

    trigger = """CREATE TRIGGER tr_"""+tableName+"""_to_synthese
                BEFORE INSERT ON bdn."""+tableName+"""
                FOR EACH ROW EXECUTE PROCEDURE bdn.tr_protocole_to_synthese();"""

    db.cur.execute(trigger)
    db.conn.commit()

    trigger = """CREATE TRIGGER fill_id_syn_"""+tableName+"""
                AFTER INSERT ON bdn."""+tableName+"""
                FOR EACH ROW EXECUTE PROCEDURE bdn.fill_id_synthese();"""
    db.cur.execute(trigger)
    db.conn.commit()





    stringCreate = "CREATE TABLE bdn.bib_champs_tortue ( id serial NOT NULL, nom_champ character varying, valeur character varying, CONSTRAINT "+tableName+"PK PRIMARY KEY (id))"
    stringCreate += addPermission
    db.cur.execute(stringCreate)
    db.conn.commit()

    sql = "INSERT INTO bdn.bib_protocole VALUES ('tortue', 'tortue', 'addObs/tortue.html', 'bib_champs_tortue')"
    db.cur.execute(sql)
    db.conn.commit()


    with open('.\\tortues.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter = ';', quotechar= '"')
        next(reader, None)

        #tableName = csvFileName.split['.'][-1]

        #create table
        for row in reader:
            #table_row = row[0].split(',')
            column_name = row[0]
            i=3
            if row[1] == 'liste_deroulante':
                liste_deroulante_tab = list()
                while i<len(row) and row[i]!= '':
                    value = row[i]
                    sql = "INSERT INTO bdn.bib_champs_tortue(nom_champ, valeur) VALUES(%s, %s) "
                    params = [column_name, value]
                    db.cur.execute(sql, params)
                    db.conn.commit()
                    i += 1

    db.closeAll()

    htmlFileName = ".\\Apps\\addObs\\static\\"+tableName+".html"
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

