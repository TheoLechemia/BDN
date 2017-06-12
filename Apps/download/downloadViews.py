# coding: utf-8
from flask import Flask, request, render_template, url_for, redirect, send_from_directory, flash, session, Blueprint, json, Response, send_file, jsonify, make_response

from ..auth import check_auth

from ..config import database
from ..config import config
from ..database import *

from .. import utils
from ..initApp import app

from datetime import datetime
import os
import csv

from psycopg2 import sql as psysql


download = Blueprint('download', __name__, static_url_path="/download", static_folder="static", template_folder="templates")
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
UPLOAD_FOLDER = PARENT_DIR+'/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@download.route('/', methods=['GET', 'POST'])
@check_auth(2)
def index():
    db = getConnexion()

    sql = "SELECT array_to_json(array_agg(row_to_json(row))) FROM (SELECT * FROM synthese.bib_projet) row"
    db.cur.execute(sql)
    protocoles = db.cur.fetchone()[0]

    sql = "SELECT array_to_json(array_agg(row_to_json(row))) FROM (SELECT * FROM utilisateurs.bib_organismes) row"
    db.cur.execute(sql)
    structures = db.cur.fetchone()[0]


    db.closeAll()
    resp = make_response(render_template('indexDownload.html', protocoles = protocoles, structures = structures, page_title=u"Télécharger des données", configuration=config))
    return resp

# @download.route('/loadTaxons/<protocole>', methods=['GET', 'POST'])
# def loadTaxons(protocole):
#     db = getConnexion()
#     if protocole == "Tout":
#         sql = """SELECT * FROM synthese.v_search_taxons"""
#     else:
#         curProtocole = "'"+protocole+"'"
#         sql = "SELECT * FROM synthese.v_search_taxons WHERE protocole = "+curProtocole
#     res = utils.sqltoDict(sql, db.cur)
#     db.closeAll()
#     return Response(json.dumps(res), mimetype='application/json')

@download.route('/loadProtocoles', methods=['GET'])
def getProtocoles():
    db = getConnexion()
    sql = "SELECT array_to_json(array_agg(row_to_json(p))) FROM (SELECT * FROM synthese.bib_projet) p"
    db.cur.execute(sql)
    return Response(json.dumps(db.cur.fetchone()[0]), mimetype='application/json')

@download.route('/search_taxon_name/<protocole>/<expr>', methods=['GET'])
def search_taxon_name(protocole, expr):
    db=getConnexion()
    tableTaxon = "taxons_"+protocole
    expr = "%"+expr+"%"
    if utils.checkForInjection(protocole):
        return Response(flask.json.dumps("Tu crois que tu vas m'injecter ??"), mimetype='application/json')
    else:
        sql = """ SELECT array_to_json(array_agg(row_to_json(r))) FROM(
                SELECT cd_nom, search_name, nom_valide, lb_nom from taxonomie.{tbl}
                WHERE search_name ILIKE %s
                ORDER BY search_name ASC 
                LIMIT 20) r"""

        formatedSql = psysql.SQL(sql).format(tbl=psysql.Identifier(tableTaxon)).as_string(db.cur)
        params = [expr]

        db.cur.execute(formatedSql, params)
        res = db.cur.fetchone()[0]
        db.closeAll()
        return Response(json.dumps(res), mimetype='application/json')



@download.route('/getObs', methods=['POST'])
def getObs():
    db = getConnexion()
    if request.method == 'POST':
        schemaReleve = 'synthese'
        if request.json['globalForm']['selectedProtocole']:
            schemaReleve = request.json['globalForm']['selectedProtocole']['nom_schema']
        sql = " SELECT * FROM {sch}.%s s "
        sql = psysql.SQL(sql).format(sch=psysql.Identifier(schemaReleve)).as_string(db.cur)
        dictSQL = utils.buildSQL(sql, 'download')
        params = dictSQL['params']
        reformatedParams = list()
        stringTupple = str()
        for p in params:
            if type(p) is int or type(p) is float:
                reformatedParams.append(p)
            if type(p) is tuple:
                if len(p)==1:
                    stringTupple = str(p).replace(',','')
                    print stringTupple
                    reformatedParams.append(stringTupple)
            if type(p) is str or type(p) is unicode:
                reformatedParams.append("'"+p+"'")

        

        paramtersPoint = list(reformatedParams)
        paramtersPoint.insert(0, 'layer_point')
        paramtersMaille = list(reformatedParams)
        paramtersMaille.insert(0, 'layer_poly')
        paramtersCSV = list(reformatedParams)
        paramtersCSV.insert(0, 'to_csv')


        sql_point = dictSQL['sql']%tuple(paramtersPoint)
        sql_poly = dictSQL['sql']%tuple(paramtersMaille)
        sql_csv = dictSQL['sql']%tuple(paramtersCSV)

        if schemaReleve == 'synthese':
            id_projet = request.json['globalForm']['selectedProtocole']['id_projet']
            sql_point += " WHERE id_projet = {id_projet}"
            sql_point = psysql.SQL(sql_point).format(id_projet=psysql.Identifier(id_projet)).as_string(db.cur)

            sql_poly += " WHERE id_projet = {id_projet}"
            sql_poly = psysql.SQL(sql_poly).format(id_projet=psysql.Identifier(id_projet)).as_string(db.cur)

            sql_csv += " WHERE id_projet = {id_projet}"
            sql_csv = psysql.SQL(sql_csv).format(id_projet=psysql.Identifier(id_projet)).as_string(db.cur)

        time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        filename = "Export_"+time
        dirPath = UPLOAD_FOLDER+"/"+filename
        point_path = dirPath+"_point"
        poly_path = dirPath+"_maille"
        csv_path = dirPath+"_csv.csv"
        debug = dirPath+"_debug"

        #construction de la requete a partir du formulaire envoye
        ###POINT###
        cmd = """ogr2ogr -f "ESRI Shapefile" """+point_path+""".shp PG:"host="""+database['HOST']+""" user="""+database['USER']+""" dbname="""+database['DATABASE_NAME']+""" password="""+database['PASSWORD']+""" " -sql  """
        cmd = cmd +'"'+sql_point+'"'
        os.system(cmd)
        ###MAILLE###
        cmd = """ogr2ogr -f "ESRI Shapefile" """+poly_path+""".shp PG:"host="""+database['HOST']+""" user="""+database['USER']+""" dbname="""+database['DATABASE_NAME']+""" password="""+database['PASSWORD']+""" " -sql  """
        cmd = cmd +'"'+sql_poly+'"'
        os.system(cmd)
        cmd_poly = cmd +'"'+sql_poly+'"'
        ###CSV###
        with open(csv_path, 'w') as f:
            outputquery = "COPY ({0}) TO STDOUT WITH CSV HEADER DELIMITER AS ';'".format(sql_csv)
            db.cur.copy_expert(outputquery, f)
        #ZIP
        utils.zipItwithCSV(dirPath, True)

        queryCount ="""WITH t_point AS (SELECT COUNT(*) AS nb_point FROM {sch}.layer_point),
                        t_poly AS  (SELECT COUNT(*) AS nb_poly  FROM {sch}.layer_poly),
                        t_total AS (SELECT COUNT(*) AS nb_csv FROM {sch}.to_csv)
                        SELECT nb_point, nb_poly, nb_csv
                        FROM t_point, t_poly, t_total"""
        queryCount = psysql.SQL(queryCount).format(sch=psysql.Identifier(schemaReleve)).as_string(db.cur)
        db.cur.execute(queryCount)
        count = db.cur.fetchone()

        db.closeAll()
        return Response(json.dumps({'filename':filename, 'count':count}), mimetype='application/json')






@download.route('/uploads/<filename>', methods=['GET'])
def uploads(filename):
    filename = filename+".zip"
    return send_from_directory(app.config['UPLOAD_FOLDER'] ,filename)
