# coding: utf-8
import os
import flask
from werkzeug.wrappers import Response 
import psycopg2
from ..config import config
from .. import utils
from ..database import *
from ..initApp import app
from ..auth import check_auth

addObs = flask.Blueprint('addObs', __name__,static_url_path="/addObs", static_folder="static", template_folder="templates")

from flask import make_response, session
from functools import wraps, update_wrapper
from datetime import datetime


def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return update_wrapper(no_cache, view)

@addObs.route('/')
@check_auth(2)
@nocache
def addObs_index():
    return flask.render_template('addObsIndex.html', configuration=config, page_title=u"Interface de saisie des données")





@addObs.route('/search_scientist_name/<table>/<expr>', methods=['GET'])
def search_scientist_name(table, expr):
    db=getConnexion()
    sql = """ SELECT array_to_json(array_agg(row_to_json(r))) FROM(
                SELECT cd_ref, lb_nom, nom_vern from taxonomie.taxons_"""+table+"""
                WHERE lb_nom ILIKE %s  
                ORDER BY lb_nom ASC 
                LIMIT 20) r"""
    params = ["%"+expr+"%"]
    db.cur.execute(sql, params)
    res = db.cur.fetchone()[0]
    db.closeAll()
    return Response(flask.json.dumps(res), mimetype='application/json')

@addObs.route('/search_vern_name/<table>/<expr>', methods=['GET'])
def search_vern_name(table, expr):
    db=getConnexion()
    sql = """ SELECT array_to_json(array_agg(row_to_json(r))) FROM(
                SELECT cd_ref, lb_nom, nom_vern from taxonomie.taxons_"""+table+""" 
                WHERE nom_vern ILIKE  %s 
                ORDER BY nom_vern ASC
                LIMIT 20) r"""
    params = ["%"+expr+"%"]
    db.cur.execute(sql, params)
    res = db.cur.fetchone()[0]
    db.closeAll()
    return Response(flask.json.dumps(res), mimetype='application/json')



@addObs.route('/loadMailles', methods=['GET', 'POST'])
def getMaille():
    db = getConnexion()
    sql = """ SELECT row_to_json(fc)
              FROM ( SELECT 
                'FeatureCollection' AS type, 
                array_to_json(array_agg(f)) AS features
                FROM(
                    SELECT 'Feature' AS type,
                   ST_ASGeoJSON(ST_TRANSFORM(m.geom,4326))::json As geometry,
                   row_to_json((SELECT l FROM(SELECT code_1km) AS l)) AS properties
                   FROM layers.mailles_1k AS m) AS f)
                AS fc; """
    db.cur.execute(sql)
    res = db.cur.fetchone()
    db.closeAll()
    return Response(flask.json.dumps(res), mimetype='application/json')


@addObs.route('/loadProtocoles', methods=['GET', 'POST'])
def getProtocoles():
    db = getConnexion()
    sql = "SELECT array_to_json(array_agg(row_to_json(p))) FROM (SELECT * FROM synthese.bib_protocole) p"
    db.cur.execute(sql)
    return Response(flask.json.dumps(db.cur.fetchone()[0]), mimetype='application/json')



@addObs.route('/loadValues/<protocole>', methods=['GET', 'POST'])
def getValues(protocole):
    db=getConnexion()
    sql = "SELECT * FROM "+protocole
    db.cur.execute(sql)
    res = db.cur.fetchall()
    currentField = res[0][3]
    finalDict = {currentField:list()}
    for r in res:
        if r[3] == currentField:
            finalDict[currentField].append(r[4])
        else:
            currentField = r[3]
            finalDict[currentField] = list()
            finalDict[currentField].append(r[4])
    return Response(flask.json.dumps(finalDict), mimetype='application/json')


def getParmeters():
    data = flask.request.json['protocoleForm']
    listKeys = list()
    listValues = list()
    for key, value in data.iteritems():
        listKeys.append(key)
        listValues.append(value)
    return {'keys': listKeys, 'values': listValues}




@addObs.route('/submit/', methods=['GET', 'POST'])
def submitObs():
    db = getConnexion()
    if flask.request.method == 'POST':
        observateur = flask.request.json['general']['observateur']
        cd_nom = flask.request.json['general']['taxon']['cd_ref']
        loc_exact = flask.request.json['general']['loc_exact']
        code_maille = str()
        loc = flask.request.json['general']['coord']
        x = str(loc['lng'])
        y = str(loc['lat'])
        point = 'POINT('+x+' '+y+')'
        code_maille = flask.request.json['general']['code_maille']

        date = flask.request.json['general']['date']
        commentaire = flask.request.json['general']['commentaire']
        protocoleObject = flask.request.json['protocole']

        fullTableName = protocoleObject['nom_complet']
        protocoleName = protocoleObject['nom_table']

        #prend le centroide de maille pou intersecter avec la foret et l'insee
        centroide = None
        if not loc_exact:
            point = None
            sql = "SELECT ST_AsText(ST_Centroid(ST_TRANSFORM(geom, 4326))) FROM layers.mailles_1k WHERE code_1km = %s "
            params = [code_maille]
            db.cur.execute(sql, params)
            res = db.cur.fetchone()
            if res != None:
                centroide = res[0]


        #foret
        sql_foret = """ SELECT ccod_frt FROM layers.perimetre_forets WHERE ST_INTERSECTS(geom,(ST_Transform(ST_PointFromText(%s, 4326),%s)))"""
        if loc_exact:
            params = [point, config['MAP']['PROJECTION']]
        else:
            params = [centroide, config['MAP']['PROJECTION']]
        db.cur.execute(sql_foret, params)
        res = db.cur.fetchone()
        ccod_frt = None 
        if res != None:
            ccod_frt = res[0]

        # #insee
        sql_insee = """ SELECT code_insee FROM layers.commune WHERE ST_INTERSECTS(geom,(ST_Transform(ST_PointFromText(%s, 4326),%s)))"""
        if loc_exact:
            params = [point, config['MAP']['PROJECTION']]
        else:
            params = [centroide, config['MAP']['PROJECTION']]
        db.cur.execute(sql_insee, params)
        res = db.cur.fetchone()
        insee = None 
        if res != None:
            insee = res[0]


        #recupere l id_structure a partir de l'info stocker dans la session
        id_structure = session['id_structure']
        valide= False

        generalValues = [observateur, date, cd_nom, point, insee, commentaire, valide, ccod_frt, loc_exact, code_maille, id_structure]


        ###protocole

        
        stringInsert = "INSERT INTO "+fullTableName+"(observateur, date, cd_nom, geom_point, insee, commentaire, valide, ccod_frt, loc_exact, code_maille, id_structure"
        stringValues = ""
        if loc_exact:
            stringValues = "VALUES (%s, %s, %s,  ST_Transform(ST_PointFromText(%s, 4326),"+str(config['MAP']['PROJECTION'])+"), %s, %s, %s, %s, %s, %s, %s"
        else:
            stringValues = "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
        keys = getParmeters()['keys']
        values = getParmeters()['values']
        for k in keys:
            stringInsert += ", "+k
            stringValues += ", %s"
        stringInsert+=")"
        stringValues+=")"
        for v in values:
            generalValues.append(v)
        params = generalValues
        sql = stringInsert+stringValues

        db.cur.execute(sql, params)
        db.conn.commit()
        db.closeAll()

    return Response(flask.json.dumps('success'), mimetype='application/json')




    