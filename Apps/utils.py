import psycopg2
import psycopg2.extras
import zipfile
import os
import flask
import config
import ast

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

    zf.write(dirPath+"_csv_point.csv", os.path.basename(dirPath+"_csv_point.csv"))
    zf.write(dirPath+"_csv_maille.csv", os.path.basename(dirPath+"_csv_maille.csv"))


def askFirstParame(sql, firstParam):
    if firstParam:
        firstParam = False
        sql = sql+" WHERE "
    else:
        sql = sql + " AND "
    return sql

def getFormParameters():
    protocole = flask.request.json['selectedProtocole']
    listTaxons = flask.request.json['listTaxons']
    firstDate = flask.request.json['when']['first']
    lastDate = flask.request.json['when']['last']
    foret = None
    commune = None
    if flask.request.json['where'] != None:
        commune = flask.request.json['where']['code_insee']    
    if flask.request.json['foret'] != None: 
        foret = flask.request.json['foret']['ccod_frt']

    # recherche taxonomique avancee
    regne = flask.request.json['regne']
    phylum = flask.request.json['phylum']
    classe = flask.request.json['classe']
    ordre = flask.request.json['ordre']
    famille = flask.request.json['famille']
    group2_inpn = flask.request.json['group2_inpn']
    habitat = flask.request.json['habitat']['id']
    protection = flask.request.json['protection']
    lr = flask.request.json['lr']['id_statut']
    structure = flask.request.json['structure']['id_structure']
    observateur = flask.request.json['observateur']['observateur']



    return {'listTaxons':listTaxons, 'firstDate':firstDate, 'lastDate':lastDate, 'commune':commune, 'foret':foret, 'regne':regne, 'phylum': phylum, 'classe':classe, 'ordre':ordre, 'famille': famille, 'group2_inpn':group2_inpn,
            'habitat': habitat, 'protection': protection, 'lr': lr, 'structure': structure, 'observateur':observateur, 'protocole':protocole }

def buildSQL():
    sql = """ SELECT ST_AsGeoJSON(ST_TRANSFORM(s.geom_point, 4326)), s.id_synthese, t.lb_nom, t.cd_nom, t.nom_vern, s.date, s.protocole, ST_AsGeoJSON(ST_TRANSFORM(l.geom, 4326)), s.code_maille, s.loc_exact, s.observateur, st.nom_structure
              FROM synthese.releve s
              LEFT JOIN layers.mailles_1k l ON s.code_maille = l.code_1km
              JOIN taxonomie.taxref t ON t.cd_nom = s.cd_nom
              JOIN utilisateur.bib_structure st ON st.id_structure = s.id_structure"""
    params = list()
    firstParam = True
    #recuperation des parametres
    formParameters = getFormParameters()
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
        params.append(tuple(formParameters['listTaxons']))
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
        firstParam = False
        sql = askFirstParame(sql, firstParam)
        sql += 't.habitat = %s'
        params.append(str(formParameters['habitat']))
    if formParameters['protection']:
        firstParam = False
        sql = askFirstParame(sql, firstParam)
        sql += 's.cd_nom IN (SELECT cd_nom from taxonomie.protection)'
    if formParameters['lr']:
        firstParam = False
        sql = askFirstParame(sql,firstParam)
        sql += 's.cd_nom IN (SELECT cd_nom from taxonomie.liste_rouge WHERE statut = %s)'
        params.append(formParameters['lr'])
    if formParameters['structure']:
        firstParam = False
        sql = askFirstParame(sql,firstParam)
        sql += 's.id_structure = %s'
        params.append(formParameters['structure'])
    if formParameters['observateur']:
        firstParam = False
        sql = askFirstParame(sql,firstParam)
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

    print sql
    return {'params': params, 'sql' :sql}
