# coding: utf-8
import os
import flask
from werkzeug.wrappers import Response 
import psycopg2
from .. import config
import ast
from .. import utils
from ..database import *
from datetime import datetime
from ..initApp import app
from werkzeug.exceptions import HTTPException, NotFound 

#synthese = flask.Blueprint('synthese', __name__)
synthese = flask.Blueprint('synthese', __name__, static_url_path="/synthese", static_folder="static", template_folder="templates")



CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
UPLOAD_FOLDER = PARENT_DIR+'/static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'Martine50='  # Change this!

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



@synthese.route("/")
def synthese_index():
    return flask.render_template('indexSynthese.html', URL_APPLICATION=config.URL_APPLICATION, page_title=u"Interface de visualisation des données")



@synthese.route('/lastObs')
@nocache
def lastObs():
    db = getConnexion()
    sql = """SELECT s.cd_nom, s.observateur, s.id_synthese, t.lb_nom, t.nom_vern, s.date, ST_AsGeoJSON(ST_TRANSFORM(s.geom_point, 4326)), ST_X(ST_Transform(geom_point, 4326)), ST_Y(ST_Transform(geom_point, 4326)), s.protocole
            FROM bdn.synthese s
            JOIN taxonomie.taxref t ON t.cd_nom = s.cd_nom
            ORDER BY date DESC
            LIMIT 50"""
    db.cur.execute(sql)
    res = db.cur.fetchall()
    data = { "type": "FeatureCollection",  "features" : list()}
    for r in res:
        date = r[5].strftime("%Y/%m/%d")
        myproperties = {'cd_nom': r[0], 'observateur': r[1],'id_synthese': r[2], 'lb_nom': r[3], 'nom_vern':r[4], 'date':date, 'x': r[7], 'y':r[8], 'protocole': r[9] }
        data['features'].append({"type": "Feature", "properties": myproperties, "geometry": ast.literal_eval( r[6]) })
    db.closeAll()

    return Response(flask.json.dumps(data), mimetype='application/json')



@synthese.route('/getObs', methods=['GET', 'POST'])
def getObs():
    db = getConnexion()    
    if flask.request.method == 'POST':
        geojson ={ "type": "FeatureCollection",  "features" : list() } 
        print utils.buildSQL()['sql']
        print utils.buildSQL()['params']
        db.cur.execute(utils.buildSQL()['sql'], utils.buildSQL()['params'])
        res = db.cur.fetchall()
        myproperties = dict()
        for r in res:
            date = r[5].strftime("%Y/%m/%d")
            myproperties = {'id_synthese': r[1], 'lb_nom':r[2], 'cd_nom': r[3], 'nom_vern': r[4], 'date': date, 'x': r[6], 'y':r[7], 'protocole': r[8], 'observateur': r[9]}
            geojson['features'].append({"type": "Feature", "properties": myproperties, "geometry": ast.literal_eval( r[0]) })
    db.closeAll()
    return Response(flask.json.dumps(geojson), mimetype='application/json')

######FORM#########
#charge le bons taxons pour la recherche par nom latin et vernaculaire en fonction du protocole choisi
@synthese.route('/loadTaxons/<protocole>', methods=['GET', 'POST'])
def loadTaxons(protocole):
    db = getConnexion()
    if protocole == "Tout":
        sql = """SELECT * FROM bdn.v_search_taxons"""
        #sql = " SELECT * FROM taxonomie.test"
    else:
        curProtocole = "'"+protocole+"'"
        sql = "SELECT * FROM bdn.v_search_taxons WHERE regne = "+curProtocole
    res = utils.sqltoDict(sql, db.cur)
    db.closeAll()
    return Response(flask.json.dumps(res), mimetype='application/json')

#charge la liste des foret
@synthese.route('/loadForets', methods=['GET', 'POST'])
def loadForets():
    db = getConnexion()
    sql = "SELECT lib_frt, ccod_frt FROM layers.perimetre_forets ORDER BY lib_frt ASC"
    res = utils.sqltoDict(sql, db.cur)
    db.closeAll()
    return Response(flask.json.dumps(res), mimetype='application/json')

#charge la liste des communes
@synthese.route('/loadCommunes', methods=['GET', 'POST'])
def loadCommunes():
    db = getConnexion()
    sql = """SELECT code_insee, nom FROM layers.commune ORDER BY nom ASC"""
    res = utils.sqltoDict(sql, db.cur)
    db.closeAll()
    return Response(flask.json.dumps(res), mimetype='application/json')

#charge la liste des group2_inpn
@synthese.route('/loadGroup2_inpn', methods = ['GET'])
def loadGroup2_inpn():
    db = getConnexion()
    listGroup = []
    sql = "SELECT DISTINCT group2_inpn FROM taxonomie.taxref ORDER BY group2_inpn ASC"
    db.cur.execute(sql)
    res = db.cur.fetchall()
    for r in res:
        listGroup.append(r[0])
    db.closeAll()
    return Response(flask.json.dumps(listGroup), mimetype='application/json')

@synthese.route('/loadTaxonomyHierachy/<rang_fils>/<rang_pere>/<rang_grand_pere>/<value_rang_grand_pere>/<value>')
def loadTaxonHierarchy(rang_fils, rang_pere, rang_grand_pere, value_rang_grand_pere, value):
    db = getConnexion()
    rang_fils = '"'+rang_fils+'"'
    rang_pere = '"'+rang_pere+'"'
    rang_grand_pere = '"'+rang_grand_pere+'"'
    if value == 'Aucun': 
        sql = "SELECT DISTINCT "+rang_fils+" FROM taxonomie.taxref WHERE "+rang_grand_pere+" = %s ORDER BY "+rang_fils+" ASC"
        params = [value_rang_grand_pere]
    else:
        sql = " SELECT DISTINCT "+rang_fils+" FROM taxonomie.taxref WHERE "+rang_pere+" = %s ORDER BY "+rang_fils+" ASC"
        params = [value]
    db.cur.execute(sql, params)
    res = db.cur.fetchall()
    listTaxons = list()
    for r in res:
        listTaxons.append(r[0])
    try:
        listTaxons.remove(None)
        listTaxons.insert(0, "Aucun")
    except ValueError:
        print 'not in list'
    db.closeAll()
    return Response(flask.json.dumps(listTaxons), mimetype='application/json')




@synthese.route('/export', methods=['GET', 'POST'])
def export():
    sqlBase = " SELECT * FROM bdn.synthese s JOIN taxonomie.taxref t ON t.cd_nom = s.cd_nom"
    if flask.request.method == 'POST':
        time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        filename = "Export_"+time
        dirPath = UPLOAD_FOLDER+"/"+filename
        #construction de la requete a partir du formulaire envoye
        sql = utils.buildSQL2OGR()

        cmd = """ogr2ogr -f "ESRI Shapefile" """+dirPath+""".shp PG:"host="""+config.HOST+""" user="""+config.USER+""" dbname="""+config.DATABASE_NAME+""" password="""+config.PASSWORD+""" " -sql  """
        cmd = cmd +'"'+sql+'"'
        print cmd

        #cree un dossier avec les shapefiles dedans (shp, shx etc..)
        os.system(cmd)
        #on zipe le tout
        utils.zipIt(dirPath)
        #on retourne le nom du dossier creer, dans la reponse du poste
        return Response(flask.json.dumps(filename), mimetype='application/json')
    return Response(flask.json.dumps("from_get"), mimetype='application/json')


@synthese.route('/uploads/<filename>')
def uploaded_file(filename):
    filename = filename+".zip"
    return flask.send_from_directory(app.config['UPLOAD_FOLDER'],filename)




@synthese.route('/ficheObs/<protocole>/<id_synthese>')
def loadFicheObs(protocole, id_synthese):
    db = getConnexion()
    if protocole == 'FAUNE':
        sql = "SELECT p.*, ST_X(ST_Transform(p.geom_point, 4326)) as x, ST_Y(ST_Transform(p.geom_point, 4326)) as y, t.lb_nom, t.nom_vern FROM bdn.faune p JOIN taxonomie.taxref t ON t.cd_nom = p.cd_nom WHERE id_synthese = %s "
    if protocole == 'FLORE':
        sql = "SELECT p.*, ST_X(ST_Transform(p.geom_point, 4326)) as x, ST_Y(ST_Transform(p.geom_point, 4326)) as y, t.lb_nom, t.nom_vern FROM bdn.flore p JOIN taxonomie.taxref t ON t.cd_nom = p.cd_nom WHERE id_synthese = %s"
    params = [id_synthese]
    res = utils.sqltoDictWithParams(sql, params, db.cur)
    return Response(flask.json.dumps(res[0]), mimetype='application/json')

@synthese.route('/modifyObs/<protocole>/<id_synthese>', methods=['GET', 'POST'])
def modifyObs(protocole, id_synthese):
    db = getConnexion()
    print protocole
    observateur = None
    if flask.request.method == 'POST':
        observateur = flask.request.json['observateur']
        sql = "UPDATE bdn."+protocole+" SET observateur = %s WHERE id_synthese = %s"
        params = [observateur, id_synthese]
        db.cur.execute(sql, params) 
        db.conn.commit()
    return Response(flask.json.dumps(observateur), mimetype='application/json')
    db.closeAll()




