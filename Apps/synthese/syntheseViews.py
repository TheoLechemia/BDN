# coding: utf-8
import os
import flask
from werkzeug.wrappers import Response 
import psycopg2
from .. import config
import ast
#import flask_login
from .. import utils
from ..database import *
#from flask_cors import CORS, cross_origin
from datetime import datetime
from ..initApp import app
app.secret_key = 'Martine50='  # Change this!
#cors = CORS(app, resources={r"/*": {"origins": "*"}})

synthese = flask.Blueprint('synthese', __name__)


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
UPLOAD_FOLDER = PARENT_DIR+'/static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'Martine50='  # Change this!



@synthese.after_request
def add_header(r):    
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=1000'
    return r

@synthese.route("/bdn-synthese")
def synthese_index():
    return flask.render_template('indexSynthese.html', URL_APPLICATION=config.URL_APPLICATION)



@synthese.route('/lastObs')
def lastObs():
    db = getConnexion()
    sql = """SELECT s.cd_nom, s.observateur, s.id_synthese, t.lb_nom, t.nom_vern, s.date, ST_AsGeoJSON(ST_TRANSFORM(s.geom_point, 4326))
            FROM bdn.synthese s
            JOIN taxonomie.taxref t ON t.cd_nom = s.cd_nom
            ORDER BY date DESC
            LIMIT 50"""
    db.cur.execute(sql)
    res = db.cur.fetchall()
    data = { "type": "FeatureCollection",  "features" : list()}
    for r in res:
        date = r[5].strftime("%d-%m-%Y")
        #date = r[5]
        myproperties = {'cd_nom': r[0], 'observateur': r[1],'id_synthese': r[2], 'lb_nom': r[3], 'nom_vern':r[4], 'date':date, }
        data['features'].append({"type": "Feature", "properties": myproperties, "geometry": ast.literal_eval( r[6]) })
    db.closeAll()

    return Response(flask.json.dumps(data), mimetype='application/json')



@synthese.route('/getObs', methods=['GET', 'POST'])
def getObs():
    db = getConnexion()
    geojson ={ "type": "FeatureCollection",  "features" : list() } 
    if flask.request.method == 'POST':
        print utils.buildSQL()['sql']
        print utils.buildSQL()['params']
        db.cur.execute(utils.buildSQL()['sql'], utils.buildSQL()['params'])
        res = db.cur.fetchall()
        myproperties = dict()
        for r in res:
            date = r[5].strftime("%d-%m-%Y")
            myproperties = {'id_synthese': r[1], 'lb_nom':r[2], 'cd_nom': r[3], 'nom_vern': r[4], 'date': date, 'observateur': r[6]}
            geojson['features'].append({"type": "Feature", "properties": myproperties, "geometry": ast.literal_eval( r[0]) })
    db.closeAll()
    return Response(flask.json.dumps(geojson), mimetype='application/json')

######FORM#########
@synthese.route('/loadTaxons/<protocole>', methods=['GET', 'POST'])
def loadTaxons(protocole):
    db = getConnexion()
    if protocole == "Tout":
        sql = """SELECT * FROM bdn.v_search_taxons"""
    else:
        curProtocole = "'"+protocole+"'"
        sql = "SELECT * FROM bdn.v_search_taxons WHERE protocole = "+curProtocole
    res = utils.sqltoDict(sql, db.cur)
    return Response(flask.json.dumps(res), mimetype='application/json')

@synthese.route('/loadForets', methods=['GET', 'POST'])
def loadForets():
    db = getConnexion()
    sql = "SELECT lib_frt, ccod_frt FROM layers.perimetre_forets ORDER BY lib_frt ASC"
    res = utils.sqltoDict(sql, db.cur)
    return Response(flask.json.dumps(res), mimetype='application/json')


@synthese.route('/loadCommunes', methods=['GET', 'POST'])
def loadCommunes():
    db = getConnexion()
    sql = """SELECT code_insee, nom FROM layers.commune ORDER BY nom ASC"""
    res = utils.sqltoDict(sql, db.cur)
    return Response(flask.json.dumps(res), mimetype='application/json')

@synthese.route('/loadTaxonomyHierachy/<rang_fils>/<rang_pere>/<value>')
def loadTaxonHierarchy(rang_fils, rang_pere, value):
    db = getConnexion()
    rang_fils = '"'+rang_fils+'"'
    rang_pere = '"'+rang_pere+'"'
    sql = " SELECT DISTINCT "+rang_fils+" FROM taxonomie.taxref WHERE "+rang_pere+" = %s"
    params = [value]
    db.cur.execute(sql, params)
    res = db.cur.fetchall()
    listTaxons = list()
    for r in res:
        listTaxons.append(r[0])
    try:
        listTaxons.remove(None)
    except ValueError:
        print 'not in list'
    return Response(flask.json.dumps(listTaxons), mimetype='application/json')


@synthese.route('/export', methods=['GET', 'POST'])
def export():
    if flask.request.method == 'POST':
        time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        filename = "Export_"+time
        dirPath = UPLOAD_FOLDER+"/"+filename
        #construction de la requete a partir du formulaire envoye
        sql = utils.buildSQL2OGR()

        cmd = """ ogr2ogr -f "ESRI Shapefile" """+dirPath+""".shp PG:"host="""+config.HOST+""" user="""+config.USER+""" dbname="""+config.DATABASE_NAME+""" password="""+config.PASSWORD+""" " -sql  """
        #cmd = 'ogr2ogr -f "ESRI Shapefile"'+dirname+'.shp PG:"host='+config.HOST+' user='+config.USER+' dbname='+config.DATABASE_NAME+' password='+config.PASSWORD+''
        cmd = cmd +'"'+sql+'"'
        print cmd
        #cree le shapefile (shp, shx etc..)
        os.system(cmd)
        #on zipe le tout
        utils.zipIt(dirPath)
        #on retourne le nom du dossier creer, dans la reponse du poste 
        return Response(flask.json.dumps(filename), mimetype='application/json')

    return Response(flask.json.dumps("from_get"), mimetype='application/json')


@synthese.route('/uploads/<filename>')
def uploaded_file(filename):
    filename = filename+".zip.zip"
    return flask.send_from_directory(app.config['UPLOAD_FOLDER'],filename)




