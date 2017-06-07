# coding: utf-8
import psycopg2
import psycopg2.extras
import zipfile
import os
import flask
from config import config
import ast
from database import *
from psycopg2 import sql as psysql
from psycopg2.extensions import AsIs

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
        try:
            zf.write(dirPath+"_maille.dbf", os.path.basename(dirPath+"_maille.dbf") )
            zf.write(dirPath+"_maille.prj", os.path.basename(dirPath+"_maille.prj"))
            zf.write(dirPath+"_maille.shx", os.path.basename(dirPath+"_maille.shx"))
            zf.write(dirPath+"_maille.shp", os.path.basename(dirPath+"_maille.shp"))
        except:
            pass
    try:
        zf.write(dirPath+"_point.dbf", os.path.basename(dirPath+"_point.dbf") )
        zf.write(dirPath+"_point.prj", os.path.basename(dirPath+"_point.prj"))
        zf.write(dirPath+"_point.shx", os.path.basename(dirPath+"_point.shx"))
        zf.write(dirPath+"_point.shp", os.path.basename(dirPath+"_point.shp"))
    except:
        pass

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
    print 'enter in htmlllllllllll'
    htmlFileName = config['APP_DIR']+"/addObs/static/"+schemaName+'.html'
    htmlFile = open(htmlFileName, "w")
    

    integerInput = "<input class='form-control' type='number' placeholder='{0}' ng-model='$ctrl.child.protocoleForm.{1}'  name='{1}' {2}> \n"
    simpleTextInput = "<input class='form-control' type='text' placeholder='{0}' ng-model='$ctrl.child.protocoleForm.{1}'  name='{1}' {2}> \n"
    checkboxInput = """<label> {0} : </label> \n
                        <input type="checkbox" name="{1}" ng-init="$ctrl.child.protocoleForm.{1}=false" ng-model="$ctrl.child.protocoleForm.{1}" {2}> \n"""
    listInput = "<div> <select class='form-control' type='text' placeholder='{0}' ng-model='$ctrl.child.protocoleForm.{1}' name='{1}' ng-options='choice as choice for choice in $ctrl.fields.{1}' {2}> <option value=""> - {0} - </option> </select>  </div> \n"
    


    for r in fieldForm:
        write = str()
        if r['obligatoire']:
            required = 'required'
            htmlWrapper = """<div class='form-group' ng-class="{{'has-error' : addObsForm.{0}.$invalid }}" >"""
            htmlWrapper = htmlWrapper.format(r['nom_champ'])
        else:
            htmlWrapper = """<div class='form-group'> \n"""
            required = ''
        if r['type_widget'] == 'Entier' or r['type_widget'] == 'Réel' :
            write  =  integerInput.format(r['lib_champ'],r['nom_champ'], required)
        if r['type_widget'] == 'Texte':
            write  =  simpleTextInput.format(r['lib_champ'],r['nom_champ'], required)
        if r['type_widget'] == 'Booléen':
            write  =  checkboxInput.format(r['lib_champ'],r['nom_champ'], required)
        if r['type_widget'] == "Liste déroulante" :
            write = listInput.format(r['lib_champ'], r['nom_champ'], required)
        finalWrite = htmlWrapper + write + "\n </div>"
        htmlFile.write(finalWrite)
    htmlFile.close()



def createProject(db, projectForm, fieldForm):
    schemaName = projectForm['nom_bdd']
    nom_table = 'releve'
    fullName = schemaName+"."+nom_table
    template = 'addObs/'+schemaName+'.html'
    bib_champs = schemaName+'.'+'bib_champs_'+schemaName

    sql = " CREATE SCHEMA {sch} AUTHORIZATION {user} "
    sql = psysql.SQL(sql).format(sch=psysql.Identifier(schemaName),user=psysql.Identifier(database['USER'])).as_string(db.cur)
    db.cur.execute(sql)
    db.conn.commit()

    #cree la table releve
    pk_name = schemaName +"_PK"
    stringCreate = """CREATE TABLE {sch}.{nom_table}
    (
      id_obs serial CONSTRAINT {pk_name} PRIMARY KEY,
      id_synthese integer,
      id_projet integer,
      id_sous_projet integer,
      observateur character varying(100) NOT NULL,
      date date NOT NULL,
      cd_nom integer NOT NULL,
      geom_point geometry(Point,"""+str(config['MAP']['PROJECTION'])+"""),
      precision character varying,
      insee character varying(10),
      altitude integer,
      commentaire character varying(150),
      comm_loc character varying(150),
      valide boolean,
      ccod_frt character varying(50),
      loc_exact boolean,
      code_maille character varying(20),
      id_structure integer,
      diffusable boolean,"""

    formatedCreate = psysql.SQL(stringCreate).format(sch=psysql.Identifier(schemaName),nom_table=psysql.Identifier(nom_table),pk_name=psysql.Identifier(pk_name)).as_string(db.cur)

    addPermission = "ALTER TABLE {sch}.{nom_table} OWNER TO {user}"
    addPermission = psysql.SQL(addPermission).format(sch=psysql.Identifier(schemaName),nom_table=psysql.Identifier(nom_table),user=psysql.Identifier(database['USER'])).as_string(db.cur)


    params = []
    for r in fieldForm:
        formatedCreate+=" {champ} %s ,"
        formatedCreate = psysql.SQL(formatedCreate).format(champ=psysql.Identifier(r['nom_champ'])).as_string(db.cur)
        params.append(AsIs(r['db_type']))
    formatedCreate = formatedCreate[0:-1]+");"
    formatedCreate += addPermission
    db.cur.execute(formatedCreate, params)
    db.conn.commit()

    #TRIGGER

    triggerName = 'tr_'+schemaName+'_to_synthese'
    trigger = """CREATE TRIGGER {trg_name}
            AFTER INSERT ON {sch}.releve
            FOR EACH ROW EXECUTE PROCEDURE synthese.tr_protocole_to_synthese();"""
    trigger = psysql.SQL(trigger).format(sch=psysql.Identifier(schemaName), trg_name=psysql.Identifier(triggerName)).as_string(db.cur)
    db.cur.execute(trigger)
    db.conn.commit()

    #BIB_CHAMPS

    tbl = 'bib_champs_'+schemaName
    sql = """CREATE TABLE {sch}.{tbl}
        (
          id_champ integer NOT NULL,
          no_spec character varying,
          nom_champ character varying,
          valeur text,
          lib_champ character varying,
          type_widget character varying,
          db_type character varying,
          obligatoire boolean,
          CONSTRAINT bib_fa_primary_key PRIMARY KEY (id_champ)
        )"""
    sql = psysql.SQL(sql).format(sch=psysql.Identifier(schemaName),tbl=psysql.Identifier(tbl)).as_string(db.cur)
    db.cur.execute(sql)
    addPermission = "ALTER TABLE "+bib_champs+" OWNER TO "+database['USER']+";"
    db.cur.execute(addPermission)
    db.conn.commit()


    for r in fieldForm:
        sql = "INSERT INTO {sch}.{tbl} VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
        sql = psysql.SQL(sql).format(sch=psysql.Identifier(schemaName),tbl=psysql.Identifier(tbl)).as_string(db.cur)
        params = [r['id_champ'], r['no_spec'], r['nom_champ'], r['valeur'], r['lib_champ'], r['type_widget'], r['db_type'], r['obligatoire']]
        db.cur.execute(sql, params)
        db.conn.commit()


def create_taxonomie_view(db, projectForm, fieldForm):
    #ajoute la liste des taxons de ce protocole dans taxhub
    #ajout dans bib_liste
    schemaName = projectForm['nom_bdd']
    query = "INSERT INTO taxonomie.bib_listes (nom_liste, picto) VALUES (%s, %s)"
    db.cur.execute(query, [projectForm['nom_projet'],'images/pictos/nopicto.gif' ])
    db.conn.commit()
    #prend le last id_liste
    db.cur.execute("SELECT MAX(id_liste) FROM taxonomie.bib_listes")
    last_id_liste = db.cur.fetchone()[0]
    #peuple la table cor_nom_liste avec tous les taxons par defaults
    query = """INSERT INTO taxonomie.cor_nom_liste (id_liste,id_nom)
    SELECT %s,n.id_nom FROM taxonomie.bib_noms n """
    db.cur.execute(query, [last_id_liste])
    #cree la vue materialise a partir de cette liste
    vue_name = 'taxons_'+schemaName
    query = """CREATE MATERIALIZED VIEW taxonomie.{vue_name} AS 
     SELECT taxonomie.find_cdref(t3.cd_nom) AS cd_ref,
        t3.cd_nom,
        t3.nom_valide,
        t3.lb_nom,
        concat(t3.lb_nom, ' = ', t3.nom_complet_html) AS search_name
       FROM taxonomie.cor_nom_liste t1
         JOIN taxonomie.bib_noms t2 ON t1.id_nom = t2.id_nom
         JOIN taxonomie.taxref t3 ON t3.cd_nom = t2.cd_nom
      WHERE t1.id_liste = %(last_id)s
    UNION
     SELECT taxonomie.find_cdref(t3.cd_nom) AS cd_ref,
        t3.cd_nom,
        t3.nom_valide,
        t3.lb_nom,
        concat(t3.nom_vern, ' = ', t3.nom_complet_html) AS search_name
       FROM taxonomie.cor_nom_liste t1
         JOIN taxonomie.bib_noms t2 ON t1.id_nom = t2.id_nom
         JOIN taxonomie.taxref t3 ON t3.cd_nom = t2.cd_nom
      WHERE t1.id_liste = %(last_id)s AND t3.nom_vern IS NOT NULL"""
    query = psysql.SQL(query).format(vue_name=psysql.Identifier(vue_name)).as_string(db.cur)
    db.cur.execute(query, {'last_id': last_id_liste})

def checkForInjection(param):
    injection = False
    dieWords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', '#', 'CREATE', '\\']
    for word in dieWords:
        if word in param or word.lower() in param:
            injection = True
    return injection


def createViewsDownload(db, projectForm, fieldForm):
    schemaName = projectForm['nom_bdd']
    #POLYGONS
    string_create_view_poly = """CREATE OR REPLACE VIEW {sch}.layer_poly AS 
    SELECT 
    t.nom_vern,
    t.lb_nom,
    f.observateur,
    f.date,
    ST_X(ST_CENTROID(ST_TRANSFORM(m.geom,4326))) AS X,
    ST_Y(ST_CENTROID(ST_TRANSFORM(m.geom,4326))) AS Y,
    f.precision,
    f.cd_nom,
    f.insee,
    f.altitude,
    f.commentaire,
    f.comm_loc,
    f.ccod_frt,
    m.id_maille,
    s.nom_organisme,
    f.id_structure,
    f.id_synthese,
    f.diffusable,"""
    string_create_view_poly = psysql.SQL(string_create_view_poly).format(sch=psysql.Identifier(schemaName)).as_string(db.cur)
    for r in fieldForm:
        string_create_view_poly += "f.{chm} ,"
        string_create_view_poly = psysql.SQL(string_create_view_poly).format(chm=psysql.Identifier(r['nom_champ'])).as_string(db.cur)
    
    string_create_view_poly = string_create_view_poly[:-1]

    string_create_view_poly += """ FROM {sch}.releve f
    JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
    JOIN layers.maille_1_2 m ON m.id_maille::text = f.code_maille::text
    LEFT JOIN utilisateurs.bib_organismes s ON f.id_structure = s.id_organisme
    WHERE f.valide = TRUE AND f.loc_exact = FALSE AND f.diffusable = TRUE;"""
    string_create_view_poly = psysql.SQL(string_create_view_poly).format(sch=psysql.Identifier(schemaName)).as_string(db.cur)

    #POINTS
    string_create_view_point = """CREATE OR REPLACE VIEW {sch}.layer_point AS 
    SELECT 
    t.nom_vern,
    t.lb_nom,
    f.observateur,
    f.date,
    ST_X(ST_TRANSFORM(f.geom_point,4326)) AS X,
    ST_Y(ST_TRANSFORM(f.geom_point,4326)) AS Y,
    f.precision,
    f.cd_nom,
    f.insee,
    f.altitude,
    f.commentaire,
    f.comm_loc,
    f.ccod_frt,
    f.geom_point,
    s.nom_organisme,
    f.id_structure,
    f.id_synthese,
    f.diffusable,"""
    string_create_view_point = psysql.SQL(string_create_view_point).format(sch=psysql.Identifier(schemaName)).as_string(db.cur)
    for r in fieldForm:
        string_create_view_point += "f.{chm} ,"
        string_create_view_point = psysql.SQL(string_create_view_point).format(chm=psysql.Identifier(r['nom_champ'])).as_string(db.cur)
    
    string_create_view_point = string_create_view_point[:-1]

    string_create_view_point += """ FROM {sch}.releve f
    JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
    LEFT JOIN utilisateurs.bib_organismes s ON f.id_structure = s.id_organisme
    WHERE f.valide = TRUE AND f.loc_exact = TRUE AND  f.diffusable = TRUE;"""
    string_create_view_point = psysql.SQL(string_create_view_point).format(sch=psysql.Identifier(schemaName)).as_string(db.cur)

    db.cur.execute(string_create_view_poly)
    db.cur.execute(string_create_view_point)
    db.conn.commit()  

    #CSV
    create_csv = """CREATE OR REPLACE VIEW {sch}.to_csv AS 
     WITH coord_point AS (
             SELECT fp.id_obs,
                st_x(st_transform(fp.geom_point, 4326)) AS x,
                st_y(st_transform(fp.geom_point, 4326)) AS y
               FROM {sch}.releve fp
              WHERE fp.loc_exact = true
            ), coord_maille AS (
             SELECT fm.id_obs,
                fm.code_maille,
                st_x(st_centroid(st_transform(m.geom, 4326))) AS x,
                st_y(st_centroid(st_transform(m.geom, 4326))) AS y
               FROM {sch}.releve fm
                 JOIN layers.maille_1_2 m ON m.id_maille::text = fm.code_maille::text
              WHERE fm.loc_exact = false
            )
     SELECT t.nom_vern,
        t.lb_nom,
        f.observateur,
        f.date,
            CASE f.loc_exact
                WHEN true THEN cp.x
                WHEN false THEN cm.x
                ELSE NULL::double precision
            END AS x,
            CASE f.loc_exact
                WHEN true THEN cp.y
                WHEN false THEN cm.y
                ELSE NULL::double precision
            END AS y,
        f.precision,
        f.loc_exact,
        f.comm_loc,
        f.cd_nom,
        f.insee,
        f.ccod_frt,
        f.altitude,
        f.geom_point,
        f.commentaire,
        s.nom_organisme,
        f.id_structure,
        f.id_synthese,
        f.diffusable,"""
    create_csv = psysql.SQL(create_csv).format(sch=psysql.Identifier(schemaName)).as_string(db.cur)

    for r in fieldForm:
        create_csv += "f.{chm} ,"
        create_csv = psysql.SQL(create_csv).format(chm=psysql.Identifier(r['nom_champ'])).as_string(db.cur)
    
    create_csv = create_csv[:-1]

    create_csv+="""FROM {sch}.releve f
     JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
     LEFT JOIN coord_point cp ON cp.id_obs = f.id_obs
     LEFT JOIN coord_maille cm ON cm.id_obs = f.id_obs
     LEFT JOIN utilisateurs.bib_organismes s ON f.id_structure = s.id_organisme AND f.diffusable = TRUE; """
    create_csv = psysql.SQL(create_csv).format(sch=psysql.Identifier(schemaName)).as_string(db.cur)

    db.cur.execute(create_csv)
    db.conn.commit()  

