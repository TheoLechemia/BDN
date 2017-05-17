# coding: utf-8
import psycopg2
import psycopg2.extras
import zipfile
import os
import flask
from config import config
import ast
from database import *

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = CURRENT_DIR+'\uploads'


#le champs geometrie doit deja etre formatte grace a ST_toGeojson
def toGeoJsonFromSQL(sql, geom, properties, cur):
    import ast
    cur.execute(sql)
    tabRes = cur.fetchall()
    res = []
    myGeoJson = {"type": "FeatureCollection",
                 "features" : list()
                }
    for row in tabRes:
        res.append(dict(row))
    
    for r in res:
        myGeom = r[geom]
        myproperties = dict()
        #build properties dict
        for p in properties:
            myproperties[p] = r[p]
        myGeoJson['features'].append({"type": "Feature", "properties": myproperties, "geometry": ast.literal_eval(myGeom)})

    return myGeoJson

def toGeoJson(sql, geom, properties, cur):
    import ast
    cur.execute(sql)
    tabRes = cur.fetchall()
    res = []
    myGeoJson = {"type": "FeatureCollection",
                 "features" : list()
                }
    for row in tabRes:
        res.append(dict(row))
    
    for r in res:
        myGeom = r[geom]
        myproperties = dict()
        #build properties dict
        for p in properties:
            myproperties[p] = r[p]
        myGeoJson['features'].append({"type": "Feature", "properties": myproperties, "geometry": ast.literal_eval(myGeom)})

    return myGeoJson

def simpleGeoJson(tab, geom, properties):
    res = list()
    myGeoJson = {"type": "FeatureCollection",
             "features" : list()
            }
    for row in tab:
        res.append(dict(row))
    
    for r in res:
        myGeom = r[geom]
        myproperties = dict()
        #build properties dict
        for p in properties:
            myproperties[p] = r[p]
        myGeoJson['features'].append({"type": "Feature", "properties": myproperties, "geometry": ast.literal_eval(myGeom)})
    return myGeoJson




def sqltoDict(sql, cur):
    cur.execute(sql)
    tabRes = cur.fetchall()
    res = []
    for row in tabRes:
        res.append(dict(row))
    return res

def sqltoDictWithParams(sql, params, cur):
    cur.execute(sql, params)
    tabRes = cur.fetchall()
    res = []
    for row in tabRes:
        res.append(dict(row))
    return res


def zipIt(dirPath, maille):
    dirPath=dirPath.split('.')[0]
    zf = zipfile.ZipFile(dirPath+'.zip', mode='w')
    if maille:
        zf.write(dirPath+"_maille.dbf", os.path.basename(dirPath+"_maille.dbf") )
        zf.write(dirPath+"_maille.prj", os.path.basename(dirPath+"_maille.prj"))
        zf.write(dirPath+"_maille.shx", os.path.basename(dirPath+"_maille.shx"))
        zf.write(dirPath+"_maille.shp", os.path.basename(dirPath+"_maille.shp"))

    zf.write(dirPath+"_point.dbf", os.path.basename(dirPath+"_point.dbf") )
    zf.write(dirPath+"_point.prj", os.path.basename(dirPath+"_point.prj"))
    zf.write(dirPath+"_point.shx", os.path.basename(dirPath+"_point.shx"))
    zf.write(dirPath+"_point.shp", os.path.basename(dirPath+"_point.shp"))


    zf.close()

def zipItwithCSV(dirPath, maille):
    dirPath=dirPath.split('.')[0]
    zf = zipfile.ZipFile(dirPath+'.zip', mode='w')
    if maille:
        zf.write(dirPath+"_maille.dbf", os.path.basename(dirPath+"_maille.dbf") )
        zf.write(dirPath+"_maille.prj", os.path.basename(dirPath+"_maille.prj"))
        zf.write(dirPath+"_maille.shx", os.path.basename(dirPath+"_maille.shx"))
        zf.write(dirPath+"_maille.shp", os.path.basename(dirPath+"_maille.shp"))

    zf.write(dirPath+"_point.dbf", os.path.basename(dirPath+"_point.dbf") )
    zf.write(dirPath+"_point.prj", os.path.basename(dirPath+"_point.prj"))
    zf.write(dirPath+"_point.shx", os.path.basename(dirPath+"_point.shx"))
    zf.write(dirPath+"_point.shp", os.path.basename(dirPath+"_point.shp"))

    zf.write(dirPath+"_csv.csv", os.path.basename(dirPath+"_csv.csv"))

firstParam = True
def askFirstParame(sql, firstParam):
    if firstParam:
        firstParam = False
        sql = sql+" WHERE "
    else:
        sql = sql + " AND "
    return sql

def getFormParameters(app):
    data = None
    if app == "synthese":
        data = flask.request.json
    if app == "download":
        data = flask.request.json['globalForm']

    protocole = data['selectedProtocole']
    listTaxons = data['listTaxons']
    firstDate = data['when']['first']
    lastDate = data['when']['last']
    foret = None
    commune = None
    if data['where'] != None:
        commune = data['where']['code_insee']    
    if data['foret'] != None: 
        foret = data['foret']['ccod_frt']

    # recherche taxonomique avancee
    regne = data['regne']
    phylum = data['phylum']
    classe = data['classe']
    ordre = data['ordre']
    famille = data['famille']
    group2_inpn = data['group2_inpn']
    habitat = data['habitat']['id']
    protection = data['protection']
    lr = data['lr']['id_statut']
    structure = data['structure']['id_organisme']
    observateur = data['observateur']['observateur']






    return {'listTaxons':listTaxons, 'firstDate':firstDate, 'lastDate':lastDate, 'commune':commune, 'foret':foret, 'regne':regne, 'phylum': phylum, 'classe':classe, 'ordre':ordre, 'famille': famille, 'group2_inpn':group2_inpn,
            'habitat': habitat, 'protection': protection, 'lr': lr, 'structure': structure, 'observateur':observateur, 'protocole':protocole }

def buildSQL(sql, app):

    params = list()
    firstParam = True
    #recuperation des parametres
    formParameters = getFormParameters(app)
    #si ça vient de la synthese on recherche le protocole, sinon non
    if app == "synthese":
        if formParameters['protocole']:
            currentProtocole = formParameters['protocole']['nom_schema']
            sql = askFirstParame(sql, firstParam)
            sql+="s.protocole = %s"
            params.append(currentProtocole)
            firstParam=False
    if len(formParameters['listTaxons']) > 0:
        sql = askFirstParame(sql, firstParam)
        firstParam = False
        sql = sql + "s.cd_nom IN %s "
        tupleTaxon = tuple(formParameters['listTaxons'])
        params.append(tupleTaxon)
    #recherche taxonomique avance
    if formParameters['regne']:
        sql = askFirstParame(sql, firstParam)
        firstParam = False
        sql = sql + "t.regne = %s"
        params.append(formParameters['regne'])
    if formParameters['phylum'] and formParameters['phylum'] != 'Aucun':
        sql = sql + " AND t.phylum = %s"
        params.append(formParameters['phylum'])
    if formParameters['classe'] and formParameters['classe'] !='Aucun':
        sql = sql + " AND t.classe = %s"
        params.append(formParameters['classe'])
    if formParameters['ordre'] and formParameters['ordre'] != 'Aucun':
        sql = sql + " AND t.ordre = %s"
        params.append(formParameters['ordre'])
    if formParameters['famille'] and formParameters['famille'] != 'Aucun':
        sql = sql + " AND t.famille = %s"
        params.append(formParameters['famille'])
    if formParameters['group2_inpn']:
        sql = askFirstParame(sql, firstParam)
        firstParam = False
        sql += " t.group2_inpn = %s"
        params.append(formParameters['group2_inpn'])
    if formParameters['habitat']:
        sql = askFirstParame(sql, firstParam)
        firstParam = False
        sql += 't.habitat = %s'
        params.append(str(formParameters['habitat']))
    if formParameters['protection']:
        sql = askFirstParame(sql, firstParam)
        firstParam = False
        sql += 's.cd_nom IN (SELECT cd_nom from taxonomie.protection)'
    if formParameters['lr']:
        sql = askFirstParame(sql,firstParam)
        firstParam = False
        sql += 's.cd_nom IN (SELECT cd_nom from taxonomie.liste_rouge WHERE statut = %s)'
        params.append(formParameters['lr'])
    if formParameters['structure']:
        sql = askFirstParame(sql,firstParam)
        firstParam = False
        sql += 's.id_structure = %s'
        params.append(formParameters['structure'])
    if formParameters['observateur']:
        sql = askFirstParame(sql,firstParam)
        firstParam = False
        sql += 's.observateur = %s'
        params.append(formParameters['observateur'])


    #recherche geographique
    if formParameters['commune']:
        sql = askFirstParame(sql, firstParam)
        sql = sql + " s.insee = %s "
        firstParam = False
        params.append(str(formParameters['commune']))
    if formParameters['foret']:
        sql = askFirstParame(sql, firstParam)
        sql = sql + " s.ccod_frt = %s "
        firstParam = False
        params.append(str(formParameters['foret']))
    #date
    if formParameters['firstDate'] and formParameters['lastDate'] :
        firstParam = False
        sql = askFirstParame(sql, firstParam)
        sql = sql + "( s.date >= %s OR s.date <= %s )"
        params.append(formParameters['firstDate'])
        params.append(formParameters['lastDate'])
    elif formParameters['firstDate']:
        firstParam = False
        sql = askFirstParame(sql,firstParam)
        sql = sql +" s.date >= %s"
        params.append(formParameters['firstDate'])
    elif formParameters['lastDate']:
        firstParam = False
        sql = askFirstParame(sql,firstParam)
        sql = sql + " s.date <= %s "
        params.append(formParameters['lastDate'])

    if app == "download":
        protocoleData = flask.request.json['protocoleForm']
        for key, value in protocoleData.iteritems():
            sql = askFirstParame(sql,firstParam)
            sql+= key+"= %s"
            firstParam = False
            params.append(value)
    print 'LAAAAAAAA'
    print sql
    print params
    return {'params': params, 'sql' :sql}

def buildGeojsonWithParams(res):
    geojsonMaille = { "type": "FeatureCollection",  "features" : list()}
    geojsonPoint = { "type": "FeatureCollection",  "features" : list()}
    for r in res:
        date = r[5].strftime("%Y/%m/%d")
        geometry = None
        #r[9] = loc_exact: check if its point or maille
        if r[9] == True:
            mypropertiesPoint = {'nom_vern': r[4], 'lb_nom':r[2], 'cd_nom': r[3], 'date': date, 'protocole': r[6], 'observateur': r[10], 'structure': r[11], 'id_synthese': r[1], 'id' : r[1]}
            try:
                geometry = ast.literal_eval( r[0])
            except ValueError:
                pass
            geojsonPoint['features'].append({"type": "Feature", "properties": mypropertiesPoint, "geometry": geometry })
        else:
            myPropertiesMaille = {'nom_vern': r[4], 'lb_nom':r[2], 'cd_nom': r[3], 'date': date, 'protocole': r[6], 'observateur': r[10], 'structure': r[11], 'id_synthese': r[1], 'id' : r[8]}
            try:
                geometry = ast.literal_eval( r[7])
            except ValueError:
                pass
            geojsonMaille['features'].append({"type": "Feature", "properties": myPropertiesMaille, "geometry": geometry })

    return {'point': geojsonPoint, 'maille': geojsonMaille}


def createTemplate(schemaName, fieldForm):
    print 'OHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH'
    htmlFileName = config['APP_DIR']+"/addObs/static/"+schemaName+'.html'
    print 'LAAAA'
    print htmlFileName
    htmlFile = open(htmlFileName, "w")

    htmlContent = """<div class='form-group'> 
                """

    integerInput = "<input class='form-control' type='number' placeholder='{0}' ng-model='$ctrl.child.protocoleForm.{0}'  name='{0}'> \n"
    simpleTextInput = "<input class='form-control' type='text' placeholder='{0}' ng-model='$ctrl.child.protocoleForm.{0}'  name='{0}'> \n"
    booleanInput = """<div'> 
                        <select class='form-control' type='text' placeholder='{0}' ng-model='$ctrl.child.protocoleForm.{0}'  > \n
                          <option value=""> -{0}- </option> 
                          <option value="True">  Oui  </option> \n
                          <option value="False">  Non  </option> \n
                        </select>\n
                      </div> \n"""
    listInput = "<div> <select class='form-control' type='text' placeholder='{0}' ng-model='$ctrl.child.protocoleForm.{0}' ng-options='choice as choice for choice in $ctrl.fields.{0}' > <option value=""> - {0} - </option> </select>  </div> \n"
    for r in fieldForm:
        if r['type_widget'] == 'number':
            write  =  integerInput.format(r['nom_champ'])
            htmlFile.write(write)
        if r['type_widget'] == 'text':
            write  =  simpleTextInput.format(r['nom_champ'])
            htmlFile.write(write)
        if r['type_widget'] == 'radio':
            write  =  booleanInput.format(r['nom_champ'])
            htmlFile.write(write)
        if r['type_widget'] == "select" :
            write = listInput.format(r['nom_champ'])
            htmlFile.write(write)
    htmlFile.close()



def createProject(db, projectForm, fieldForm):
    schemaName = projectForm['nom_bdd']
    nom_table = 'releve'
    fullName = schemaName+"."+nom_table
    template = 'addObs/'+schemaName+'.html'
    bib_champs = schemaName+'.'+'bib_champs_'+schemaName

    sql = " CREATE SCHEMA "+schemaName+" AUTHORIZATION "+ database['USER']
    db.cur.execute(sql)
    db.conn.commit()

    stringCreate = """CREATE TABLE """+fullName+""" 
    (
      id_obs serial CONSTRAINT """+schemaName+"""_PK PRIMARY KEY,
      id_synthese integer,
      id_projet integer,
      id_sous_projet integer,
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

    for r in fieldForm:
        stringCreate+=" "+ r['nom_champ']+" "+r['db_type']+","
    stringCreate = stringCreate[0:-1]+");"
    stringCreate += addPermission
    db.cur.execute(stringCreate)
    db.conn.commit()

    #TRIGGER
    trigger = """CREATE TRIGGER tr_"""+schemaName+"""_to_synthese
            AFTER INSERT ON """+fullName+"""
            FOR EACH ROW EXECUTE PROCEDURE synthese.tr_protocole_to_synthese();"""
    db.cur.execute(trigger)
    db.conn.commit()

    #BIB_CHAMPS
    sql = """CREATE TABLE """+bib_champs+"""
        (
          id_champ integer NOT NULL,
          no_spec character varying,
          nom_champ character varying,
          valeur text,
          lib_champ character varying,
          type_widget character varying,
          db_type character varying,
          CONSTRAINT bib_fa_primary_key PRIMARY KEY (id_champ)
        )"""
    db.cur.execute(sql)
    addPermission = "ALTER TABLE "+bib_champs+" OWNER TO "+database['USER']+";"
    db.cur.execute(addPermission)
    db.conn.commit()


    for r in fieldForm:
        sql = "INSERT INTO """+bib_champs+" VALUES(%s, %s, %s, %s, %s, %s, %s)"
        params = [r['id_champ'], r['no_spec'], r['nom_champ'], r['valeur'], r['lib_champ'], r['type_widget'], r['db_type']]
        db.cur.execute(sql, params)
        db.conn.commit()

