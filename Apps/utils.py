import psycopg2
import psycopg2.extras
import zipfile
import os
import flask
import config

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




def sqltoDict(sql, cur):
    cur.execute(sql)
    tabRes = cur.fetchall()
    res = []
    for row in tabRes:
        res.append(dict(row))
    return res


def zipIt(dirPath):
    zf = zipfile.ZipFile(dirPath+'.zip', mode='w')
    zf.write(dirPath+".dbf", os.path.basename(dirPath+".dbf") )
    zf.write(dirPath+".prj", os.path.basename(dirPath+".prj"))
    zf.write(dirPath+".shx", os.path.basename(dirPath+".shx"))
    zf.write(dirPath+".shp", os.path.basename(dirPath+".shp"))

    # for (archiveDirPath, dirNames, fileNames) in os.walk(dirPath):
    #         for fileName in fileNames:
    #             filePath = os.path.join(archiveDirPath, fileName)
    #             zf.write(filePath, os.path.basename(filePath))
    zf.close()


def askFirstParame(sql, firstParam):
    if firstParam:
        firstParam = False
        sql = sql+" WHERE "
    else:
        sql = sql + " AND "
    return sql


def getFormParameters():
    listTaxons = flask.request.json['listTaxons']
    firstDate = flask.request.json['when']['first']
    lastDate = flask.request.json['when']['last']
    commune = flask.request.json['where']['code_insee']
    foret = flask.request.json['foret']['ccod_frt']

    # recherche taxonomique avancee
    regne = flask.request.json['regne']
    phylum = flask.request.json['phylum']
    classe = flask.request.json['classe']
    ordre = flask.request.json['ordre']
    famille = flask.request.json['famille']

    return {'listTaxons':listTaxons, 'firstDate':firstDate, 'lastDate':lastDate, 'commune':commune, 'foret':foret, 'regne':regne, 'phylum': phylum, 'classe':classe, 'ordre':ordre, 'famille': famille  }

def buildSQL():
    sql = """ SELECT ST_AsGeoJSON(ST_TRANSFORM(s.geom_point, 4326)), s.id_synthese, t.lb_nom, t.cd_nom, t.nom_vern, s.date
              FROM bdn.synthese s
              JOIN taxonomie.taxref t ON t.cd_nom = s.cd_nom"""
    params = list()
    firstParam = True
    #recuperation des parametres
    formParameters = getFormParameters()

    if formParameters['listTaxons']:
        firstParam = False
        sql = sql + " WHERE s.cd_nom IN %s "
        params.append(tuple(formParameters['listTaxons']))
    if formParameters['regne']:
        firstParam = False
        sql = sql + " WHERE t.regne = %s"
        params.append(formParameters['regne'])
    if formParameters['phylum'] and formParameters['phylum'] != 'Aucun':
        sql = askFirstParame(sql, firstParam)
        firstParam = False
        sql = sql + " t.phylum = %s"
        params.append(formParameters['phylum'])
    if formParameters['classe'] and formParameters['classe'] !='Aucun':
        sql = askFirstParame(sql, firstParam)
        firstParam = False
        sql = sql + " t.classe = %s"
        params.append(formParameters['classe'])
    if formParameters['ordre'] and formParameters['ordre'] != 'Aucun':
        sql = askFirstParame(sql, firstParam)
        firstParam = False
        sql = sql + " t.ordre = %s"
        params.append(formParameters['ordre'])
    if formParameters['famille'] and formParameters['famille'] != 'Aucun':
        sql = askFirstParame(sql, firstParam)
        firstParam = False
        sql = sql + " t.famille = %s"
        params.append(formParameters['famille'])

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
    if formParameters['firstDate'] and formParameters['lastDate'] :
        sql = askFirstParame(sql, firstParam)
        sql = sql + "( s.date >= %s OR s.date <= %s )"
        params.append(formParameters['firstDate'])
        params.append(formParameters['lastDate'])
    elif formParameters['firstDate']:
        if firstParam:
            sql = askFirstParame(sql,firstParam)
        sql = sql +" s.date >= %s"
        params.append(firstDate)
    elif formParameters['lastDate']:
        sql = askFirstParame(sql,firstParam)
        sql = sql + " s.date <= %s "
        params.append(lastDate)
    return {'params': params, 'sql' :sql}


def buildSQL2OGR():
    sql = " SELECT * FROM bdn.synthese s JOIN taxonomie.taxref t ON t.cd_nom = s.cd_nom"
    params = list()
    firstParam = True
    #recuperation des parametres
    formParameters = getFormParameters()


    if formParameters['listTaxons']:
        firstParam = False
        stringCdNom = "("
        for cd_nom in formParameters['listTaxons']:
            stringCdNom += str(cd_nom)+","
        stringCdNom= stringCdNom[:-1]
        stringCdNom += " )"
        print 'OHHHHHHHHHHHHHH'
        print stringCdNom
        sql = sql + " WHERE s.cd_nom IN "+ stringCdNom

    if formParameters['commune']:
        commune = "'" + formParameters['commune'] +"'"
        sql = askFirstParame(sql,firstParam)
        firstParam = False
        sql = sql + " s.insee = " +commune

    if formParameters['foret']:
        foret = "'"+formParameters['foret']+"'"
        sql = askFirstParame(sql, firstParam)
        firstParam = False
        sql = sql + " s.ccod_frt = "+foret

    if formParameters['firstDate'] and formParameters['lastDate'] :
        firstDate = "'" + formParameters['firstDate'] +"'"
        lastDate = "'" + formParameters['lastDate'] +"'"
        sql = askFirstParame(sql,firstParam)
        firstParam = False
        sql = sql + "( s.date >="+firstDate+" OR s.date <="+lastDate+" )"

    elif formParameters['firstDate']:
        firstDate = "'" + formParameters['firstDate'] +"'"
        sql = askFirstParame(sql,firstParam)
        sql = sql +" s.date >="+ firstDate
    elif formParameters['lastDate']:
        lastDate = "'" + formParameters['lastDate'] +"'"
        sql = askFirstParame(sql,firstParam)
        sql = sql + " s.date <="+lastDate
    return sql