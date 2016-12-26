import psycopg2
import psycopg2.extras
import zipfile
import os
import flask



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

def buildSQL():
    cd_nom1= None
    cd_nom2 = None
    commune = None
    foret = None
    firstDate = None
    lastDate = None
    sql = """ SELECT ST_AsGeoJSON(ST_TRANSFORM(s.geom_point, 4326)), s.id_synthese, t.lb_nom, t.cd_nom, t.nom_vern, s.date, s.observateur
              FROM bdn.synthese s
              JOIN taxonomie.taxref t ON t.cd_nom = s.cd_nom"""
    params = list()
    firstParam = True
    #recuperation des parametres
    if flask.request.json['lb_nom'] != None:
        cd_nom1 = flask.request.json['lb_nom']['cd_nom']
    if flask.request.json['nom_vern'] != None:
        cd_nom2 = flask.request.json['nom_vern']['cd_nom']
    if flask.request.json['when'] != None :
        firstDate = flask.request.json['when']['first']
        lastDate = flask.request.json['when']['last']
    if flask.request.json['where'] != None:
        commune = flask.request.json['where']['code_insee']
    if flask.request.json['foret'] != None:
        foret = flask.request.json['foret']['ccod_frt']

    if cd_nom1:
        firstParam = False
        sql = sql + " WHERE s.cd_nom = %s "
        params.append(cd_nom1)
    elif cd_nom2:
        firstParam = False
        sql = sql + " WHERE s.cd_nom = %s "
        params.append(cd_nom2)
    if commune:
        sql = askFirstParame(sql, firstParam)
        firstParam = False
        sql = sql + " s.insee = %s "
        params.append(str(commune))
    if foret:
        sql = askFirstParame(sql, firstParam)
        firstParam = False
        sql = sql + " s.ccod_frt = %s "
        params.append(str(foret))
    if firstDate and lastDate :
        sql = askFirstParame(sql, firstParam)
        firstParam = False
        sql = sql + "( s.date >= %s OR s.date <= %s )"
        params.append(firstDate)
        params.append(lastDate)
    elif firstDate:
        if firstParam:
            sql = askFirstParame(sql,firstParam)
        sql = sql +" s.date >= %s"
        params.append(firstDate)
    elif lastDate:
        sql = askFirstParame(sql,firstParam)
        sql = sql + " s.date <= %s "
        params.append(lastDate)
    print sql
    return {'params': params, 'sql' :sql}


def buildSQL2OGR():
    cd_nom1= None
    cd_nom2 = None
    commune = None
    foret = None
    firstDate = None
    lastDate = None
    sql = " SELECT * FROM bdn.synthese s JOIN taxonomie.taxref t ON t.cd_nom = s.cd_nom"
    params = list()
    firstParam = True
    #recuperation des parametres
    if flask.request.json['lb_nom'] != None:
        cd_nom1 = flask.request.json['lb_nom']['cd_nom']
    if flask.request.json['nom_vern'] != None:
        cd_nom2 = flask.request.json['nom_vern']['cd_nom']
    if flask.request.json['when'] != None :
        firstDate = flask.request.json['when']['first']
        lastDate = flask.request.json['when']['last']
    if flask.request.json['where'] != None:
        commune = flask.request.json['where']['code_insee']
    if flask.request.json['foret'] != None:
        foret = flask.request.json['foret']['ccod_frt']
    goodCdnom = None

    if cd_nom1:
        goodCdnom = str(cd_nom1)
    elif cd_nom2:
        goodCdnom = str(cd_nom2)


    if goodCdnom:
        firstParam = False
        sql = sql + " WHERE s.cd_nom = "+ goodCdnom
    if commune:
        commune = "'" + commune +"'"
        sql = askFirstParame(sql,firstParam)
        firstParam = False
        sql = sql + " s.insee = " +commune
    if foret:
        foret = "'"+foret+"'"
        sql = askFirstParame(sql, firstParam)
        firstParam = False
        sql = sql + " s.ccod_frt = "+foret
    if firstDate and lastDate :
        firstDate = "'" + firstDate +"'"
        lastDate = "'" + lastDate +"'"
        sql = askFirstParame(sql,firstParam)
        firstParam = False
        sql = sql + "( s.date >="+firstDate+" OR s.date <="+lastDate+" )"
    elif firstDate:
        firstDate = "'" + firstDate +"'"
        sql = askFirstParame(sql,firstParam)
        firstParam = False
        sql = sql +" s.date >="+ firstDate
    elif lastDate:
        lastDate = "'" + lastDate +"'"
        sql = askFirstParame(sql,firstParam)
        firstParam = False
        sql = sql + " s.date <="+lastDate
    return sql