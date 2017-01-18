# coding: utf-8
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
    myGeoJson = {"type": "FeatureCollection",
             "features" : list()
            }
    for r in tab:
        myGeom = r[geom]
        print myGeom
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


def zipIt(dirPath):
    zf = zipfile.ZipFile(dirPath+'.zip', mode='w')
    zf.write(dirPath+".dbf", os.path.basename(dirPath+".dbf") )
    zf.write(dirPath+".prj", os.path.basename(dirPath+".prj"))
    zf.write(dirPath+".shx", os.path.basename(dirPath+".shx"))
    zf.write(dirPath+".shp", os.path.basename(dirPath+".shp"))

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


    return {'listTaxons':listTaxons, 'firstDate':firstDate, 'lastDate':lastDate, 'commune':commune, 'foret':foret, 'regne':regne, 'phylum': phylum, 'classe':classe, 'ordre':ordre, 'famille': famille, 'group2_inpn':group2_inpn }

def buildSQL():
    sql = """ SELECT ST_AsGeoJSON(ST_TRANSFORM(s.geom_point, 4326)), s.id_synthese, t.lb_nom, t.cd_nom, t.nom_vern, s.date, ST_X(ST_Transform(geom_point, 4326)), ST_Y(ST_Transform(geom_point, 4326)), s.protocole, s.observateur, s.valide
              FROM bdn.synthese s
              JOIN taxonomie.taxref t ON t.cd_nom = s.cd_nom"""
    params = list()
    firstParam = True
    #recuperation des parametres
    formParameters = getFormParameters()

    if len(formParameters['listTaxons']) > 0:
        firstParam = False
        sql = sql + " WHERE s.cd_nom IN %s "
        params.append(tuple(formParameters['listTaxons']))
    #recherche taxonomique avance
    if formParameters['regne']:
        firstParam = False
        sql = sql + " WHERE t.regne = %s"
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
    firstParam = True
    #recuperation des parametres
    formParameters = getFormParameters()


    if len(formParameters['listTaxons']) > 0:
        firstParam = False
        stringCdNom = "("
        for cd_nom in formParameters['listTaxons']:
            stringCdNom += str(cd_nom)+","
        stringCdNom= stringCdNom[:-1]
        stringCdNom += " )"
        sql = sql + " WHERE s.cd_nom IN "+ stringCdNom

    #recherche taxonomique avancée
    if formParameters['regne']:
        sql = askFirstParame(sql,firstParam)
        firstParam = False
        regne = "'"+formParameters['regne']+"'"
        sql += " t.regne = "+regne
    if formParameters['phylum'] and formParameters['phylum'] != 'Aucun':
        phylum = "'"+formParameters['phylum']+"'"
        sql += " AND t.phylum = "+ phylum
    if formParameters['classe'] and formParameters['classe'] !='Aucun':
        classe = "'"+formParameters['classe']+"'"
        sql += " AND t.classe = "+classe
        params.append(formParameters['classe'])
    if formParameters['ordre'] and formParameters['ordre'] != 'Aucun':
        ordre ="'"+formParameters['ordre']+"'"
        sql += " AND t.ordre = "+ordre
    if formParameters['famille'] and formParameters['famille'] != 'Aucun':
        famille = "'"+formParameters['famille']+"'"
        sql += " AND t.famille = "+famille
        params.append(formParameters['famille'])

    if formParameters['group2_inpn']:
        sql = askFirstParame(sql, firstParam)
        firstParam = False
        group2_inpn = "'"+formParameters['group2_inpn']+"'"
        sql += " t.group2_inpn = "+ group2_inpn

    #recherche geographique
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

    #recherche date
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

    sql = askFirstParame(sql, firstParam)
    sql += " s.valide = true"
    print sql
    return sql