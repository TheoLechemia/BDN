# coding: utf-8
from flask import render_template, json, Blueprint, request
#from ..initApp import app
from .. import config
from ..database import *
from .. import utils
from werkzeug.wrappers import Response 
from ..auth import check_auth


validation = Blueprint('validation', __name__, static_url_path="/validation", static_folder="static", template_folder="templates")



@validation.route("/")
@check_auth(3)
def indexValidation():
    db = getConnexion()
    sql = """ SELECT f."""+config.ID_OBSERVATION+""" as id_synthese, f.observateur, f.protocole, f.cd_nom, t.nom_vern, t.lb_nom, f.date, ST_AsGeoJSON(ST_TRANSFORM("""+config.GEOM_NAME+""", 4326)) AS geom
     FROM """+config.TABLE_NAME+""" f
     JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
     WHERE f.valide = FALSE AND f.loc_exact = TRUE"""
    print sql
    res = utils.sqltoDict(sql, db.cur)
    nom_vern = None
    for r in res:
        if r['nom_vern'] == None:
            r['nom_vern'] = '-'
        r['nom_vern'] = r['nom_vern'].decode('utf-8')

    geojson = utils.simpleGeoJson(res, 'geom', ['id_synthese'])
    print res
    print 'LAAAAAAA'
    print geojson
    db.closeAll()
    return render_template('indexValidation.html', URL_APPLICATION=config.URL_APPLICATION, taxList=res, geojson = geojson, page_title=u"Interface de validation des données")




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


@validation.route('/validate', methods=['GET', 'POST'])
def validate():
    db = getConnexion()
    #id_synt = str(id_synt)
    tab = list()
    id_synt = tuple()
    if request.method == 'POST':
        id_synt = request.json['validate']
        if type(id_synt) != str:
            tab.append(id_synt)
            tupleSynth = tuple(tab)
        else:
            tupleSynth = tuple(id_synt)
        print "OHHH"
        print id_synt
        sql = """UPDATE synthese.syntheseff
                 SET valide = TRUE
                 WHERE id_synthese IN %s;"""
        param = [tupleSynth]
        db.cur.execute(sql,param) 
        db.conn.commit()
    db.closeAll()
    return json.dumps({'success':True, 'id_synthese':id_synt}), 200, {'ContentType':'application/json'}
