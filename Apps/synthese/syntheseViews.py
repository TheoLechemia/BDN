# coding: utf-8
import os
import flask
from werkzeug.wrappers import Response 
import psycopg2
from ..config import config, secret_key
import ast
from .. import utils
from ..database import *
from datetime import datetime
from ..initApp import app
from werkzeug.exceptions import HTTPException, NotFound 
import geojson2shp
from ..auth import check_auth
from psycopg2 import sql as psysql

synthese = flask.Blueprint('synthese', __name__, static_url_path="/synthese", static_folder="static", template_folder="templates")



CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
UPLOAD_FOLDER = PARENT_DIR+'/static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = secret_key

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
@check_auth(1)
def synthese_index():
    resp = flask.make_response(flask.render_template('indexSynthese.html', configuration=config, page_title=u"Interface de visualisation des données"))
    return resp



@synthese.route('/lastObs', methods=['GET'])
@nocache
def lastObs():
    db = getConnexion()
    sql = """ SELECT ST_AsGeoJSON(ST_TRANSFORM(s.geom_point, 4326)), s.id_synthese, t.lb_nom, t.cd_nom, t.nom_vern, s.date, p.nom_projet, ST_AsGeoJSON(ST_TRANSFORM(l.geom, 4326)), s.code_maille, s.loc_exact, s.observateur, u.nom_organisme
              FROM synthese.releve s
              JOIN taxonomie.taxref t ON t.cd_nom = s.cd_nom
              LEFT JOIN utilisateurs.bib_organismes u ON u.id_organisme = s.id_structure
              LEFT JOIN layers.maille_1_2 l ON s.code_maille = l.id_maille
              JOIN synthese.bib_projet p ON s.id_projet = p.id_projet
              ORDER BY date DESC
              LIMIT 50"""
    db.cur.execute(sql)
    res = db.cur.fetchall()
    geojsons = utils.buildGeojsonWithParams(res)                   
    db.closeAll()
    return Response(flask.json.dumps({'point':geojsons['point'],'maille':geojsons['maille']}), mimetype='application/json')



@synthese.route('/getObs', methods=['POST'])
def getObs():
    db = getConnexion()    
    if flask.request.method == 'POST':
        geojsonMaille ={ "type": "FeatureCollection",  "features" : list() }
        geojsonPoint ={ "type": "FeatureCollection",  "features" : list() }
        sql = """ SELECT ST_AsGeoJSON(ST_TRANSFORM(s.geom_point, 4326)), s.id_synthese, t.lb_nom, t.cd_nom, t.nom_vern, s.date, p.nom_projet, ST_AsGeoJSON(ST_TRANSFORM(l.geom, 4326)), s.code_maille, s.loc_exact, s.observateur, st.nom_organisme
              FROM synthese.releve s
              LEFT JOIN layers.maille_1_2 l ON s.code_maille = l.id_maille
              JOIN taxonomie.taxref t ON t.cd_nom = s.cd_nom
              LEFT JOIN utilisateurs.bib_organismes st ON st.id_organisme = s.id_structure
              LEFT JOIN synthese.bib_projet p ON s.id_projet = p.id_projet"""
        sqlAndParams = utils.buildSQL(sql, "synthese")
        db.cur.execute(sqlAndParams['sql'], sqlAndParams['params'])
        res = db.cur.fetchall()
        myproperties = dict()
        geojsons = utils.buildGeojsonWithParams(res)
    db.closeAll()
    return Response(flask.json.dumps({'point':geojsons['point'],'maille':geojsons['maille']}), mimetype='application/json')

######FORM#########
#charge le bons taxons pour la recherche par nom latin et vernaculaire en fonction du protocole choisi
@synthese.route('/loadTaxons/<expr>/<protocole>', methods=['GET', 'POST'])
def loadTaxons(expr, protocole):
    db=getConnexion()
    if protocole == "undefined" or protocole == 'Tout':
        sql = """ SELECT array_to_json(array_agg(row_to_json(r))) FROM(
                SELECT cd_nom, search_name, nom_valide, lb_nom from synthese.vm_search_taxons
                WHERE search_name ILIKE %s
                ORDER BY search_name ASC 
                LIMIT 20) r"""
        params = ["%"+expr+"%"]
    else:       
        sql = """ SELECT array_to_json(array_agg(row_to_json(r))) FROM(
                    SELECT cd_nom, search_name, nom_valide, lb_nom from synthese.vm_search_taxons
                    WHERE search_name ILIKE %s  AND regne = %s
                    ORDER BY search_name ASC 
                    LIMIT 20) r"""
        params = ["%"+expr+"%", protocole]
    db.cur.execute(sql, params)
    res = db.cur.fetchone()[0]
    db.closeAll()
    return Response(flask.json.dumps(res), mimetype='application/json')

@synthese.route('/loadProtocoles', methods=['GET', 'POST'])
def getProtocoles():
    db = getConnexion()
    sql = "SELECT array_to_json(array_agg(row_to_json(p))) FROM (SELECT * FROM synthese.bib_projet) p"
    db.cur.execute(sql)
    return Response(flask.json.dumps(db.cur.fetchone()[0]), mimetype='application/json')

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

#charge la liste des typologie: group inpn, habitat, liste_rouge, observateur et structure
@synthese.route('/loadTypologgie', methods = ['GET'])
def loadTypologgie():
    db = getConnexion()
    sql = "SELECT DISTINCT group2_inpn FROM taxonomie.taxref ORDER BY group2_inpn ASC"
    group2_inpn = utils.sqltoDict(sql, db.cur)
    sql = "SELECT * FROM taxonomie.bib_habitat"
    habitat = utils.sqltoDict(sql, db.cur)
    sql = "SELECT * FROM taxonomie.bib_liste_rouge"
    listeRouge = utils.sqltoDict(sql, db.cur)
    sql = "SELECT array_agg(row_to_json (r)) FROM (SELECT DISTINCT observateur FROM synthese.releve ORDER BY observateur ASC)r"
    db.cur.execute(sql)
    observateurs = db.cur.fetchone()[0]
    sql = "SELECT array_agg(row_to_json (r)) FROM (SELECT DISTINCT nom_organisme, id_organisme FROM utilisateurs.bib_organismes ORDER BY id_organisme ASC)r"
    db.cur.execute(sql)
    structures = db.cur.fetchone()[0]
    db.closeAll()
    return Response(flask.json.dumps({'group2_inpn':group2_inpn, 'habitat': habitat, 'listeRouge':listeRouge, 'observateurs': observateurs, 'structures': structures}), mimetype='application/json')

    

@synthese.route('/loadTaxonomyHierachy/<rang_fils>/<rang_pere>/<rang_grand_pere>/<value_rang_grand_pere>/<value>')
def loadTaxonHierarchy(rang_fils, rang_pere, rang_grand_pere, value_rang_grand_pere, value):
    db = getConnexion()
    if value == 'Aucun': 
        query = "SELECT DISTINCT {rngFils} FROM taxonomie.taxref WHERE {rngGrd} = %s ORDER BY {rngFils} ASC"
        formatedQuery = psysql.SQL(query).format(rngFils=psysql.Identifier(rang_fils), rngGrd=psysql.Identifier(rang_grand_pere)).as_string(db.cur)
        params = [value_rang_grand_pere]
    else:
        query = " SELECT DISTINCT {rngFils} FROM taxonomie.taxref WHERE {rngPere} = %s ORDER BY {rngFils} ASC"
        formatedQuery = psysql.SQL(query).format(rngFils=psysql.Identifier(rang_fils), rngPere=psysql.Identifier(rang_pere)).as_string(db.cur)
        params = [value]
    db.cur.execute(formatedQuery, params)
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
    if flask.request.method == 'POST':
        geojsonPoint = flask.request.json['point']
        geojsonMaille = flask.request.json['maille']

        time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        filename = "Export_"+time
        completePath = UPLOAD_FOLDER+"/"+filename
        
        #construction des shapes
        maille = None
        geojson2shp.export(completePath+"_point.shp", geojsonPoint, 'point')
        if len(geojsonMaille['features'])> 0:
            maille = True
            geojson2shp.export(completePath+"_maille.shp", geojsonMaille, 'polygon')

        #on zipe le tout
        utils.zipIt(completePath, maille)
        #on retourne le nom du dossier creer, dans la reponse du poste
        return Response(flask.json.dumps(filename), mimetype='application/json')
    return Response(flask.json.dumps("from_get"), mimetype='application/json')


@synthese.route('/uploads/<filename>')
@check_auth(2)
def uploaded_file(filename):
    filename = filename+".zip"
    return flask.send_from_directory(UPLOAD_FOLDER ,filename)


# @synthese.route('/ficheObs/<protocole>/<id_synthese>')
# def loadFicheObs(protocole, id_synthese):
#     db = getConnexion()
#     if protocole == 'FAUNE':
#         sql = "SELECT p.*, ST_X(ST_Transform(p.geom_point, 4326)) as x, ST_Y(ST_Transform(p.geom_point, 4326)) as y, t.lb_nom, t.nom_vern FROM bdn.faune p JOIN taxonomie.taxref t ON t.cd_nom = p.cd_nom WHERE id_synthese = %s "
#     if protocole == 'FLORE':
#         sql = "SELECT p.*, ST_X(ST_Transform(p.geom_point, 4326)) as x, ST_Y(ST_Transform(p.geom_point, 4326)) as y, t.lb_nom, t.nom_vern FROM bdn.flore p JOIN taxonomie.taxref t ON t.cd_nom = p.cd_nom WHERE id_synthese = %s"
#     params = [id_synthese]
#     res = utils.sqltoDictWithParams(sql, params, db.cur)
#     return Response(flask.json.dumps(res[0]), mimetype='application/json')

# @synthese.route('/modifyObs/<protocole>/<id_synthese>', methods=['GET', 'POST'])
# def modifyObs(protocole, id_synthese):
#     db = getConnexion()
#     print protocole
#     print id_synthese
#     observateur = None
#     if flask.request.method == 'POST':
#         observateur = flask.request.json['observateur']
#         sql = """UPDATE bdn."""+protocole+""" SET observateur = %s WHERE id_synthese = %s;
#                  UPDATE bdn.synthese SET observateur = %s WHERE id_synthese = %s"""
#         params = [observateur, id_synthese,observateur, id_synthese]
#         db.cur.execute(sql, params)
#         cd_nom = flask.request.json['taxon']['cd_nom']
#         print cd_nom
#         sql = """UPDATE bdn."""+protocole+""" SET cd_nom = %s WHERE id_synthese = %s;
#                 UPDATE bdn.synthese SET cd_nom = %s WHERE id_synthese = %s """
#         params = [cd_nom, id_synthese, cd_nom, id_synthese]
#         db.cur.execute(sql, params)
#         loc = flask.request.json['loc']
#         x = str(loc['x'])
#         y = str(loc['y'])
#         point = 'POINT('+x+' '+y+')'
#         sql = """UPDATE bdn."""+protocole+""" SET geom_point = ST_Transform(ST_PointFromText(%s, 4326),%s) WHERE id_synthese = %s;
#                 UPDATE bdn.synthese SET geom_point = ST_Transform(ST_PointFromText(%s, 4326),%s) WHERE id_synthese = %s;"""
#         params = [point, config.PROJECTION, id_synthese, point, config.PROJECTION, id_synthese]
#         db.cur.execute(sql, params)
#         db.conn.commit()
#     db.closeAll()
#     return Response(flask.json.dumps(loc), mimetype='application/json')


##### DETAIL OBS ########

#Renvoie le detail d'une observation a partir de son ID_SYNTHESE
@synthese.route('/detailsObs/<id_synthese>/', methods=['GET'])
def detailsObs(id_synthese):
    db = getConnexion()
    sql= """SELECT t.nom_vern, t.lb_nom, c.nom AS nom_commune, s.id_synthese, s.observateur, to_char(s.date, 'DD-MM-YYYY') AS date, u.nom_organisme, p.nom_projet
          FROM synthese.releve s
          JOIN taxonomie.taxref t ON t.cd_nom = s.cd_nom
          JOIN layers.commune c ON c.code_insee = s.insee
          LEFT JOIN utilisateurs.bib_organismes u ON s.id_structure=u.id_organisme
          JOIN synthese.bib_projet p ON s.id_projet = p.id_projet
          WHERE s.id_synthese = %s"""
    param = [id_synthese]
    res = utils.sqltoDictWithParams(sql, param, db.cur)
    if len(res)>0:
        res = res[0]
    db.closeAll()
    return Response(flask.json.dumps(res), mimetype='application/json')



@synthese.route('/detailsTaxonomie/<cd_nom>/', methods=['GET'])
def detailsTaxonomie(cd_nom):
    db = getConnexion()
    sql= """SELECT nom_vern, nom_valide, group1_inpn, ordre, famille, cd_nom
            FROM taxonomie.taxref
            WHERE cd_nom = %s"""
    param = [cd_nom]
    res = utils.sqltoDictWithParams(sql, param, db.cur)
    if len(res)>0:
        res = res[0]
    db.closeAll()
    return Response(flask.json.dumps(res), mimetype='application/json')


@synthese.route('/detailsReglementation/<cd_nom>/', methods=['GET'])
def detailsReglementation(cd_nom):
    db = getConnexion()
    sql= """SELECT a.arrete, a.url, a.type_protection, a.url_inpn, p.cd_nom
            FROM taxonomie.taxref_protection_especes p
            JOIN taxonomie.taxref_protection_articles a ON a.cd_protection = p.cd_protection
            WHERE p.cd_nom = %s"""
    param = [cd_nom]
    protection = None
    protection = utils.sqltoDictWithParams(sql, param, db.cur)
    sql = """SELECT r.id_categorie_france, br.type_statut, r.liste_rouge_source
            FROM taxonomie.taxref_liste_rouge_fr r
            JOIN taxonomie.bib_liste_rouge br ON br.id_statut = r.id_categorie_france
            WHERE r.cd_nom = %s"""
    lr = utils.sqltoDictWithParams(sql, param, db.cur)
    db.closeAll()
    return Response(flask.json.dumps({'lr': lr, 'protection': protection}), mimetype='application/json')
