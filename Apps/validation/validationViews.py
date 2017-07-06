# coding: utf-8
from flask import render_template, json, Blueprint, request, make_response
#from ..initApp import app
from ..config import config
from ..database import *
from .. import utils
from werkzeug.wrappers import Response 
from ..auth import check_auth
import ast
from flask import session
from psycopg2 import sql as psysql

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


validation = Blueprint('validation', __name__, static_url_path="/validation", static_folder="static", template_folder="templates")



@validation.route('/')
@check_auth(3)
def indexValidation():
    db = getConnexion()

    sql = "SELECT array_to_json(array_agg(row_to_json(row))) FROM (SELECT * FROM synthese.bib_projet WHERE saisie_possible = TRUE) row"
    db.cur.execute(sql)
    protocoles = db.cur.fetchone()[0]
    db.closeAll()
    return make_response(render_template('indexValidation.html', protocoles=protocoles, page_title=u"Interface de validation des données"))

    


@validation.route("/<int:id_projet>")
@check_auth(3)
def mapValidation(id_projet):
    db = getConnexion()
    id_structure = session['id_structure']
    sql = """ SELECT ST_AsGeoJSON(ST_TRANSFORM(s.geom_point, 4326)), s.id_synthese, t.lb_nom, t.cd_nom, t.nom_vern, s.date, p.nom_bdd AS protocole, ST_AsGeoJSON(ST_TRANSFORM(l.geom, 4326)), s.code_maille, s.loc_exact, s.observateur
              FROM synthese.releve s
              JOIN taxonomie.taxref t ON t.cd_nom = s.cd_nom
              LEFT JOIN layers.maille_1_2 l ON s.code_maille = l.id_maille
              JOIN synthese.bib_projet p ON p.id_projet = s.id_projet 
              WHERE s.valide = false AND s.id_projet = %s AND id_structure = %s
              ORDER BY s.date DESC"""
    param = [id_projet, id_structure]
    db.cur.execute(sql, param)
    res = db.cur.fetchall()
    geojson = { "type": "FeatureCollection",  "features" : list()}
    nom_vern = unicode()
    protocole = str()
    for r in res:
        protocole = r[6]
        if r[4] == None:
            nom_vern = '-'
        else:
            nom_vern = r[4].decode('utf-8')
        date = r[5].strftime("%Y/%m/%d")
        mypropertiesPoint = {'id_synthese': r[1], 'lb_nom':r[2], 'cd_nom': r[3], 'nom_vern': nom_vern, 'date': date, 'protocole': r[6], 'id' : r[1], 'observateur': r[10]}
        myPropertiesMaille = {'id_synthese': r[1], 'lb_nom':r[2], 'cd_nom': r[3], 'nom_vern': nom_vern, 'date': date, 'protocole': r[6], 'id' : r[8], 'observateur': r[10]}

        #r[9] = loc_exact: check if its point or maille
        if r[9] == True:
            try:
                geometry = ast.literal_eval( r[0])
            except ValueError:
                geometry = None
            geojson['features'].append({"type": "Feature", "properties": mypropertiesPoint, "geometry": geometry })
        else:
            try:
                geometry = ast.literal_eval( r[7])
            except ValueError:
                    geometry = None
            geojson['features'].append({"type": "Feature", "properties": myPropertiesMaille, "geometry": geometry })
    db.closeAll()
    return make_response(render_template('mapValidation.html', configuration=config, taxList=res, geojson=geojson, protocole=protocole, page_title=u"Interface de validation des données"))




@validation.route('/delete/<id_synt>/<protocole>')
@check_auth(3)
def deleteRow(id_synt, protocole):
    db = getConnexion()
    id_synt = str(id_synt)
    sql = "DELETE FROM synthese.releve WHERE id_synthese = %s; "
    param = [id_synt]
    db.cur.execute(sql, param) 

    query = "DELETE FROM {schm}.releve WHERE id_synthese = %s; "
    formatedQuery = psysql.SQL(query).format(schm=psysql.Identifier(protocole)).as_string(db.cur)
    db.cur.execute(formatedQuery, param) 
    db.conn.commit()
    db.closeAll()
    return Response(json.dumps({'success':True, 'id_synthese':id_synt}), 200, {'ContentType':'application/json'})


@validation.route('/validate/', methods=['GET', 'POST'])
@check_auth(3)
def validate():
    db = getConnexion()
    tab = list()
    id_synt = tuple()
    if request.method == 'POST':
        id_synt = request.json['validate']
        protocole = request.json['protocole']
        print type(id_synt)
        if type(id_synt) is list:
            intTab = list()
            for i in id_synt:
                intTab.append(int(i))
            tupleSynth = tuple(intTab)
        else:
            tupleSynth = tuple(int(id_synt))

        query = """UPDATE synthese.releve
                 SET valide = TRUE
                 WHERE id_synthese IN %s ;
                 UPDATE {schm}.releve
                 SET valide = TRUE 
                 WHERE id_synthese IN %s ;"""
        formatedQuery = psysql.SQL(query).format(schm=psysql.Identifier(protocole)).as_string(db.cur)
        param = [tupleSynth, tupleSynth]
        db.cur.execute(formatedQuery, param)

        
        db.conn.commit()
    db.closeAll()
    return Response(json.dumps({'success':True, 'id_synthese':id_synt}), 200, {'ContentType':'application/json'})
