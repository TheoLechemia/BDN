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
import ast


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





@addObs.route('/search_taxon_name/<table>/<expr>', methods=['GET'])
def search_taxon_name(table, expr):
    db=getConnexion()
    sql = """ SELECT array_to_json(array_agg(row_to_json(r))) FROM(
                SELECT cd_ref, search_name, nom_valide from taxonomie.taxons_"""+table+"""
                WHERE search_name ILIKE %s  
                ORDER BY search_name ASC 
                LIMIT 20) r"""
    params = ["%"+expr+"%"]
    db.cur.execute(sql, params)
    res = db.cur.fetchone()[0]
    db.closeAll()
    return Response(flask.json.dumps(res), mimetype='application/json')



@addObs.route('/loadMailles', methods=['GET'])
def getMaille():
    db = getConnexion()
    sql = """ SELECT row_to_json(fc)
              FROM ( SELECT 
                'FeatureCollection' AS type, 
                array_to_json(array_agg(f)) AS features
                FROM(
                    SELECT 'Feature' AS type,
                   ST_ASGeoJSON(ST_TRANSFORM(m.geom,4326))::json As geometry,
                   row_to_json((SELECT l FROM(SELECT id_maille) AS l)) AS properties
                   FROM layers.maille_1_2 AS m WHERE m.taille_maille='1') AS f)
                AS fc; """
    db.cur.execute(sql)
    res = db.cur.fetchone()
    db.closeAll()
    return Response(flask.json.dumps(res), mimetype='application/json')

#charge les mailles de la bounding box courante de la carte
@addObs.route('/load_bounding_box_mailles/<limit>', methods=['GET'])
def getboundingMaille(limit):
    db = getConnexion()
    sql = 'SELECT ST_TRANSFORM(ST_MakeEnvelope('+limit+', 4326),32620);'
    db.cur.execute(sql)
    bounding = db.cur.fetchone()
    sql = """ SELECT row_to_json(fc)
              FROM ( SELECT 
                'FeatureCollection' AS type, 
                array_to_json(array_agg(f)) AS features
                FROM(
                    SELECT 'Feature' AS type,
                   ST_ASGeoJSON(ST_TRANSFORM(m.geom,4326))::json As geometry,
                   row_to_json((SELECT l FROM(SELECT id_maille) AS l)) AS properties
                   FROM layers.maille_1_2 AS m WHERE m.taille_maille='1' AND ST_Within(m.geom,ST_TRANSFORM(ST_MakeEnvelope("""+limit+""", 4326),32620))  ) AS f)
                AS fc; """
    db.cur.execute(sql)
    res = db.cur.fetchone()
    db.closeAll()
    return Response(flask.json.dumps(res), mimetype='application/json')


@addObs.route('/loadProtocoles', methods=['GET', 'POST'])
def getProtocoles():
    db = getConnexion()
    sql = "SELECT array_to_json(array_agg(row_to_json(p))) FROM (SELECT * FROM synthese.bib_projet WHERE saisie_possible = TRUE) p"
    db.cur.execute(sql)
    return Response(flask.json.dumps(db.cur.fetchone()[0]), mimetype='application/json')



@addObs.route('/loadValues/<protocole>', methods=['GET'])
def getValues(protocole):
    db=getConnexion()
    sql = "SELECT * FROM "+protocole
    db.cur.execute(sql)
    res = db.cur.fetchall()
    finalDict = dict()
    for r in res:
        dictValues = ast.literal_eval(r[3])
        finalDict[r[2]] = dictValues['values']
    return Response(flask.json.dumps(finalDict), mimetype='application/json')


def getParmeters():
    data = flask.request.json['protocoleForm']
    listKeys = list()
    listValues = list()
    for key, value in data.iteritems():
        listKeys.append(key)
        listValues.append(value)
    return {'keys': listKeys, 'values': listValues}



@addObs.route('/submit/', methods=['POST'])
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
        comm_loc = flask.request.json['general']['comm_loc']
        protocoleObject = flask.request.json['protocole']

        fullTableName = protocoleObject['nom_schema']+"."+protocoleObject['nom_table']
        protocoleName = protocoleObject['nom_table']
        id_projet = protocoleObject['id_projet']


        #prend le centroide de maille pour intersecter avec la foret et l'insee
        centroid = None
        if not loc_exact:
            point = None
            sql = "SELECT ST_AsText(ST_Centroid(ST_TRANSFORM(geom, 4326))) FROM layers.maille_1_2 WHERE id_maille = %s "
            params = [code_maille]
            db.cur.execute(sql, params)
            res = db.cur.fetchone()
            if res != None:
                centroid = res[0]


        #foret
        sql_foret = """ SELECT ccod_frt FROM layers.perimetre_forets WHERE ST_INTERSECTS(geom,(ST_Transform(ST_GeomFromText(%s, 4326),%s)))"""
        if loc_exact:
            params = [point, config['MAP']['PROJECTION']]
        else:
            params = [centroid, config['MAP']['PROJECTION']]
        db.cur.execute(sql_foret, params)
        res = db.cur.fetchone()
        ccod_frt = None 
        if res != None:
            ccod_frt = res[0]

        # #insee
        sql_insee = """ SELECT code_insee FROM layers.commune WHERE ST_INTERSECTS(geom,(ST_Transform(ST_GeomFromText(%s, 4326),%s)))"""
        if loc_exact:
            params = [point, config['MAP']['PROJECTION']]
        else:
            params = [centroid, config['MAP']['PROJECTION']]
        db.cur.execute(sql_insee, params)
        res = db.cur.fetchone()
        insee = None 
        if res != None:
            insee = res[0]


        #recupere l id_structure a partir de l'info stocker dans la session
        id_structure = session['id_structure']
        valide= False

        generalValues = [id_projet,observateur, date, cd_nom, point, insee, commentaire, valide, ccod_frt, loc_exact, code_maille, id_structure, comm_loc]


        ###protocole 
        stringInsert = "INSERT INTO "+fullTableName+"(id_projet, observateur, date, cd_nom, geom_point, insee, commentaire, valide, ccod_frt, loc_exact, code_maille, id_structure, comm_loc"
        stringValues = ""
        if loc_exact:
            stringValues = "VALUES (%s, %s, %s, %s,  ST_Transform(ST_PointFromText(%s, 4326),"+str(config['MAP']['PROJECTION'])+"), %s, %s, %s, %s, %s, %s, %s, %s"
        else:
            stringValues = "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
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




    