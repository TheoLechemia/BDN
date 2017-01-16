# coding: utf-8
import os
import flask
from werkzeug.wrappers import Response 
import psycopg2
from .. import config
from .. import utils
from ..database import *
from ..initApp import app

addObs = flask.Blueprint('addObs', __name__, static_url_path="/addObs", static_folder="static", template_folder="templates")

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

@addObs.route('/submit/<protocole>', methods=['GET', 'POST'])
def sublmitObs(protocole):
    db = getConnexion()
    if flask.request.method == 'POST':
        observateur = flask.request.json['general']['observateur']
        cd_nom = flask.request.json['general']['taxon']['cd_nom']
        loc = flask.request.json['general']['coord']
        x = str(loc['lng'])
        y = str(loc['lat'])
        point = 'POINT('+x+' '+y+')'
        date = flask.request.json['general']['date']
        if protocole == 'flore':
            abondance = flask.request.json['flore']['abondance']
            nb_pied_exact = flask.request.json['flore']['nb_pied_exact']
            nb_pied_approx = flask.request.json['flore']['nb_pied_approx']
            stade_dev = flask.request.json['flore']['stade_dev']
        protocole = protocole.upper()


        #foret
        sql_foret = """ SELECT code_insee FROM layers.commune WHERE ST_INTERSECTS(geom,(ST_Transform(ST_PointFromText(%s, 4326),%s)))"""
        params = [point, config.PROJECTION]
        db.cur.execute(sql_foret, params)
        res = db.cur.fetchone()
        ccod_frt = None 
        if res != None:
            ccod_frt = res[0]

        # #insee
        sql_insee = """ SELECT code_insee FROM layers.commune WHERE ST_INTERSECTS(geom,(ST_Transform(ST_PointFromText(%s, 4326),%s)))"""
        params = [point, config.PROJECTION]
        db.cur.execute(sql_insee, params)
        res = db.cur.fetchone()
        insee = None 
        if res != None:
            insee = res[0]

        


        sql = '''INSERT INTO bdn.flore (protocole, observateur, date, cd_nom, insee, ccod_frt, abondance, nb_pied_approx, nb_pied, stade_dev, geom_point, valide  )
        VALUES (%s, %s, %s, %s, %s,%s,%s,%s, %s, %s, ST_Transform(ST_PointFromText(%s, 4326),32620), %s )'''
        params = [protocole, observateur, date, cd_nom, insee, ccod_frt, abondance, nb_pied_approx, nb_pied_exact, stade_dev, point, 'false']
        db.cur.execute(sql, params)
        db.conn.commit()

        print observateur
        print cd_nom
        print x
        print y
    return Response(flask.json.dumps('success'), mimetype='application/json')
