# coding: utf-8
from flask import render_template, json, Blueprint
#from ..initApp import app
from .. import config
from ..database import *
from .. import utils
from werkzeug.wrappers import Response 


validation = Blueprint('validation', __name__)



@validation.route("/")
def indexValidation():
    db = getConnexion()
    sql = """ SELECT f.id_synthese, f.observateur, f.protocole, f.cd_nom, t.nom_vern, t.lb_nom, f.date
     FROM bdn.synthese f
     JOIN taxonomie.taxref t ON t.cd_nom = f.cd_nom
     WHERE f.valide = FALSE """
    db.cur.execute(sql)
    mytab = db.cur.fetchall()
    taxList = list() 
    nom_vern = None
    for t in mytab:
        if t[4] == None:
            nom_vern = '-'
        else:
            nom_vern = t[4]
        temp = [t[0], t[2], nom_vern.decode('utf-8'), t[5], t[6], t[1], t[3]]
        taxList.append(temp)
    db.closeAll()
    return render_template('indexValidation.html', URL_APPLICATION=config.URL_APPLICATION, taxList=taxList, page_title=u"Interface de validation des données")


@validation.route('/geojson')
def getGeojson():
    db = getConnexion()
    sql= """ SELECT  ST_AsGeoJSON(ST_TRANSFORM(geom_point, 4326)) AS geom, id_synthese 
             FROM bdn.synthese
             WHERE valide = FALSE """

    myGeoJson = utils.toGeoJson(sql=sql, geom='geom', properties=['id_synthese'], cur=db.cur)
    db.closeAll()

    return Response(json.dumps(myGeoJson), mimetype='application/json')


@validation.route('/delete/<id_synt>')
def deleteRow(id_synt):
    db = getConnexion()
    id_synt = str(id_synt)
    sql = """DELETE FROM bdn.synthese WHERE id_synthese = %s; """
    param = [id_synt]
    db.cur.execute(sql, param) 
    db.conn.commit()
    db.closeAll()
    return json.dumps({'success':True, 'id_synthese':id_synt}), 200, {'ContentType':'application/json'}


@validation.route('/validate', methods=['GET', 'POST'])
def validate():
    db = getConnexion()
    #id_synt = str(id_synt)
    id_synt = None
    if request.method == 'POST':
        id_synt = request.json['validate']
        id_synt = tuple(id_synt)
        sql = """UPDATE bdn.synthese
                 SET valide = TRUE
                 WHERE id_synthese IN %s;"""
        param = [id_synt]
        db.cur.execute(sql,param) 
        db.conn.commit()
    db.closeAll()
    return json.dumps({'success':True, 'id_synthese':id_synt}), 200, {'ContentType':'application/json'}
