# coding: utf-8
from flask import render_template, json, Blueprint, request
#from ..initApp import app
from ..config import config
from ..database import *
from .. import utils
from werkzeug.wrappers import Response 
from ..auth import check_auth
import ast
from flask import session

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


validation = Blueprint('validation', __name__, static_url_path="/validation", static_folder="static", template_folder="templates")



@validation.route('/')
@check_auth(3)
def indexValidation():
    db = getConnexion()

    sql = "SELECT array_to_json(array_agg(row_to_json(row))) FROM (SELECT * FROM synthese.bib_protocole) row"
    db.cur.execute(sql)
    protocoles = db.cur.fetchone()[0]
    db.closeAll()
    return render_template('indexValidation.html', protocoles=protocoles, page_title=u"Interface de validation des données")

    


@validation.route("/<protocole>")
@check_auth(3)
def mapValidation(protocole):
    db = getConnexion()
    id_structure = session['id_structure']
    sql = """ SELECT ST_AsGeoJSON(ST_TRANSFORM(s.geom_point, 4326)), s.id_synthese, t.lb_nom, t.cd_nom, t.nom_vern, s.date, s.protocole, ST_AsGeoJSON(ST_TRANSFORM(l.geom, 4326)), s.code_maille, s.loc_exact, s.observateur
              FROM synthese.syntheseff s
              JOIN taxonomie.taxref t ON t.cd_nom = s.cd_nom
              LEFT JOIN layers.mailles_1k l ON s.code_maille = l.code_1km
              WHERE s.valide = false AND s.protocole = %s AND id_structure = %s"""
    param = [protocole, id_structure]
    db.cur.execute(sql, param)
    res = db.cur.fetchall()
    geojson = { "type": "FeatureCollection",  "features" : list()}
    nom_vern = unicode()
    for r in res:
        if r[4] == None:
            nom_vern = '-'
        else:
            nom_vern = r[4].decode('utf-8')
        date = r[5].strftime("%Y/%m/%d")
        mypropertiesPoint = {'id_synthese': r[1], 'lb_nom':r[2], 'cd_nom': r[3], 'nom_vern': nom_vern, 'date': date, 'protocole': r[6], 'id' : r[1], 'observateur': r[10]}
        myPropertiesMaille = {'id_synthese': r[1], 'lb_nom':r[2], 'cd_nom': r[3], 'nom_vern': nom_vern, 'date': date, 'protocole': r[6], 'id' : r[8], 'observateur': r[10]}

        #r[9] = loc_exact: check if its point or maille
        if r[9] == True:
            geojson['features'].append({"type": "Feature", "properties": mypropertiesPoint, "geometry": ast.literal_eval( r[0]) })
        else:
            geojson['features'].append({"type": "Feature", "properties": myPropertiesMaille, "geometry": ast.literal_eval( r[7]) })
    db.closeAll()
    return render_template('mapValidation.html', configuration=config, taxList=res, geojson=geojson, protocole=protocole, page_title=u"Interface de validation des données")






@validation.route('/delete/<id_synt>/<protocole>')
def deleteRow(id_synt, protocole):
    db = getConnexion()
    id_synt = str(id_synt)
    sql = "DELETE FROM synthese.syntheseff WHERE id_synthese = %s; "
    param = [id_synt]
    db.cur.execute(sql, param) 

    sql = "DELETE FROM "+protocole+".releve WHERE id_synthese = %s; "
    db.cur.execute(sql, param) 
    db.conn.commit()
    db.closeAll()
    return json.dumps({'success':True, 'id_synthese':id_synt}), 200, {'ContentType':'application/json'}


@validation.route('/validate/', methods=['GET', 'POST'])
def validate():
    db = getConnexion()
    #id_synt = str(id_synt)
    tab = list()
    id_synt = tuple()
    if request.method == 'POST':
        id_synt = request.json['validate']
        protocole = request.json['protocole']
        print 'lAAAAAAAAAAAAAAAAAAAAA'
        print type(id_synt)
        if type(id_synt) is list:
            intTab = list()
            for i in id_synt:
                intTab.append(int(i))
            tupleSynth = tuple(intTab)
        else:
            tupleSynth = tuple(int(id_synt))

        sql = """UPDATE synthese.syntheseff
                 SET valide = TRUE
                 WHERE id_synthese IN %s ;
                 UPDATE """+protocole+""".releve
                 SET valide = TRUE 
                 WHERE id_synthese IN %s ;"""
        param = [tupleSynth, tupleSynth]
        db.cur.execute(sql,param)

        
        db.conn.commit()
    db.closeAll()
    return json.dumps({'success':True, 'id_synthese':id_synt}), 200, {'ContentType':'application/json'}
