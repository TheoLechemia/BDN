# coding: utf-8
import os
import flask
from werkzeug.wrappers import Response 
import psycopg2
from .. import config
from .. import utils
from ..database import *
from ..initApp import app

addObs = flask.Blueprint('addObs', __name__,static_url_path="/addObs", static_folder="static", template_folder="templates")

from flask import make_response
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
@nocache
def addObs_index():
    return flask.render_template('addObsIndex.html', URL_APPLICATION=config.URL_APPLICATION, page_title=u"Interface de saisie des données")





@addObs.route('/search_scientist_name/<table>/<expr>', methods=['GET'])
def search_scientist_name(table, expr):
    db=getConnexion()
    sql = """ SELECT array_to_json(array_agg(row_to_json(r))) FROM(
                SELECT cd_ref, lb_nom, nom_vern from taxonomie.taxons_"""+table+"""
                WHERE lb_nom ILIKE %s LIMIT 20) r"""
    params = [expr+"%"]
    db.cur.execute(sql, params)
    res = db.cur.fetchone()[0]
    db.closeAll()
    return Response(flask.json.dumps(res), mimetype='application/json')

@addObs.route('/search_vern_name/<table>/<expr>', methods=['GET'])
def search_vern_name(table, expr):
    db=getConnexion()
    sql = """ SELECT array_to_json(array_agg(row_to_json(r))) FROM(
                SELECT cd_ref, lb_nom, nom_vern from taxonomie.taxons_"""+table+"""
                WHERE nom_vern ILIKE  %s LIMIT 20) r"""
    params = [expr+"%"]
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

@addObs.route('/submit/<protocole>', methods=['GET', 'POST'])
def submitObs(protocole):
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
        print "LAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        print point

        date = flask.request.json['general']['date']

        #prend le centroide de maille pou intersecter avec la foret et l'insee
        centroide = None
        if not loc_exact:
            sql = "SELECT ST_AsText(ST_Centroid(ST_TRANSFORM(geom, 4326))) FROM layers.mailles_1k WHERE code_1km = %s "
            params = [code_maille]
            db.cur.execute(sql, params)
            res = db.cur.fetchone()
            if res != None:
                centroide = res[0]


        #foret
        sql_foret = """ SELECT ccod_frt FROM layers.perimetre_forets WHERE ST_INTERSECTS(geom,(ST_Transform(ST_PointFromText(%s, 4326),%s)))"""
        if loc_exact:
            params = [point, config.PROJECTION]
        else:
            params = [centroide, config.PROJECTION]
        db.cur.execute(sql_foret, params)
        res = db.cur.fetchone()
        ccod_frt = None 
        if res != None:
            ccod_frt = res[0]

        # #insee
        sql_insee = """ SELECT code_insee FROM layers.commune WHERE ST_INTERSECTS(geom,(ST_Transform(ST_PointFromText(%s, 4326),%s)))"""
        if loc_exact:
            params = [point, config.PROJECTION]
        else:
            params = [centroide, config.PROJECTION]
        db.cur.execute(sql_insee, params)
        res = db.cur.fetchone()
        insee = None 
        if res != None:
            insee = res[0]
        
        if protocole == 'flore':
            abondance = flask.request.json['flore']['abondance']
            nb_pied_exact = flask.request.json['flore']['nb_pied_exact']
            nb_pied_approx = flask.request.json['flore']['nb_pied_approx']
            stade_dev = flask.request.json['flore']['stade_dev']
            protocole = protocole.upper()
            if loc_exact:
                sql = '''INSERT INTO bdn.flore (protocole, observateur, date, cd_nom, insee, ccod_frt, abondance, nb_pied_approx, nb_pied, stade_dev, geom_point, valide, loc_exact  )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_Transform(ST_PointFromText(%s, 4326),32620), %s, %s )'''
                params = [protocole, observateur, date, cd_nom, insee, ccod_frt, abondance, nb_pied_approx, nb_pied_exact, stade_dev, point, 'false', loc_exact]
            else: 
                sql = '''INSERT INTO bdn.flore (protocole, observateur, date, cd_nom, insee, ccod_frt, abondance, nb_pied_approx, nb_pied, stade_dev, valide, loc_exact, code_maille  )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )'''
                params = [protocole, observateur, date, cd_nom, insee, ccod_frt, abondance, nb_pied_approx, nb_pied_exact, stade_dev, 'false', loc_exact, code_maille]                
            db.cur.execute(sql, params)
            db.conn.commit()

        if protocole == 'faune':
            type_obs = flask.request.json['faune']['type_obs']
            effectif = flask.request.json['faune']['effectif']
            comportement = flask.request.json['faune']['comportement']
            nb_individu = flask.request.json['faune']['nb_individu']
            nb_male = flask.request.json['faune']['nb_male']
            nb_femelle = flask.request.json['faune']['nb_femelle']
            nb_jeune = flask.request.json['faune']['nb_jeune']
            nb_non_identife = flask.request.json['faune']['nb_non_identifie']
            protocole = protocole.upper()
            sql = '''INSERT INTO bdn.faune (protocole, observateur, date, cd_nom, insee, ccod_frt, type_obs, nb_individu_approx, comportement, nb_non_identife, nb_male, nb_femelle, nb_jeune, trace, geom_point, valide )
                   VALUES (%s, %s, %s, %s, %s,%s,%s, %s, %s, %s, %s, %s, %s, %s, ST_Transform(ST_PointFromText(%s, 4326),32620), %s )'''
            params = [protocole, observateur, date, cd_nom, insee, ccod_frt, type_obs, nb_individu, comportement, nb_non_identife, nb_male, nb_femelle, nb_jeune, trace, point, 'false']
            cur.execute(sql, params)
            conn.commit()

    return Response(flask.json.dumps('success'), mimetype='application/json')