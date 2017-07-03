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
import sys


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


@download.route('/loadProtocoles', methods=['GET'])
def getProtocoles():
    db = getConnexion()
    sql = "SELECT array_to_json(array_agg(row_to_json(p))) FROM (SELECT * FROM synthese.bib_projet ORDER BY id_projet DESC) p"
    db.cur.execute(sql)
    return Response(json.dumps(db.cur.fetchone()[0]), mimetype='application/json')

@download.route('/search_taxon_name/<int:id_projet>/<expr>', methods=['GET'])
def search_taxon_name(id_projet, expr):
    db=getConnexion()
    expr = "%"+expr+"%"
    #tous les projets = 99999
    if id_projet != 99999:
        sql = """ SELECT array_to_json(array_agg(row_to_json(r))) FROM(
                SELECT DISTINCT cd_nom, search_name, nom_valide, lb_nom from taxonomie.taxons_synthese
                WHERE search_name ILIKE %s AND id_projet = %s
                ORDER BY search_name ASC 
                LIMIT 20) r"""
        params = [expr, id_projet]
        db.cur.execute(sql, params)
    else:
        sql = """ SELECT array_to_json(array_agg(row_to_json(r))) FROM(
        SELECT DISTINCT cd_nom, search_name, nom_valide, lb_nom from taxonomie.taxons_synthese
        WHERE search_name ILIKE %s
        ORDER BY search_name ASC 
        LIMIT 20) r"""
        params = [expr]
        db.cur.execute(sql, params)
    res = db.cur.fetchone()[0]
    db.closeAll()
    return Response(json.dumps(res), mimetype='application/json')



@download.route('/getObs', methods=['POST'])
def getObs():
    db = getConnexion()
    if request.method == 'POST':
        schemaReleve = request.json['globalForm']['selectedProtocole']['nom_schema']
        tables = ['layer_point', 'layer_poly', 'to_csv']
        sqlTab = list()
        params = list()
        #on construit trois fois le SQL pour chacune des tables (meme si les parametres ne changent pas, le nom de la table change...)
        for t in tables:
            sql = " SELECT * FROM {sch}.{tbl} s "
            sql = psysql.SQL(sql).format(sch=psysql.Identifier(schemaReleve),tbl=psysql.Identifier(t)).as_string(db.cur)
            dictSQL = utils.buildSQL(sql, 'download')
            params = dictSQL['params']
            firstParam = dictSQL['firstParam']
            sqlTab.append(dictSQL['sql'])

        sql_point = db.cur.mogrify(sqlTab[0], params)
        sql_poly = db.cur.mogrify(sqlTab[1], params)
        sql_csv = db.cur.mogrify(sqlTab[2], params)

        id_projet = request.json['globalForm']['selectedProtocole']['id_projet']
        if schemaReleve == 'synthese' and id_projet != 99999:
            
            sql_point = utils.askFirstParame(sql_point,firstParam)
            sql_point += " id_projet = %s"
            sql_point = db.cur.mogrify(sql_point, [id_projet])
            print 'LAAAAAAAAAA'
            print db.cur.mogrify(sql_point, [id_projet])

            sql_poly = utils.askFirstParame(sql_poly,firstParam)
            sql_poly += " id_projet = %s"
            sql_poly = db.cur.mogrify(sql_poly, [id_projet])

            sql_csv = utils.askFirstParame(sql_csv,firstParam)
            sql_csv += " id_projet = %s"
            sql_csv = db.cur.mogrify(sql_csv, [id_projet])


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

        db.closeAll()
        return Response(json.dumps({'filename':filename}), mimetype='application/json')






@download.route('/uploads/<filename>', methods=['GET'])
def uploads(filename):
    filename = filename+".zip"
    return send_from_directory(app.config['UPLOAD_FOLDER'] ,filename)
