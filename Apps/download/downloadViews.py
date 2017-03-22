# coding: utf-8
from flask import Flask, request, render_template, url_for, redirect, send_from_directory, flash, session, Blueprint, json, Response

from ..auth import check_auth

from ..config import database
from ..database import *

from .. import utils

from datetime import datetime
import os
import csv


download = Blueprint('download', __name__, static_url_path="/download", static_folder="static", template_folder="templates")
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
UPLOAD_FOLDER = PARENT_DIR+'/static/uploads'

@download.route('/', methods=['GET', 'POST'])
@check_auth(2)
def index():
    db = getConnexion()

    sql = "SELECT array_to_json(array_agg(row_to_json(row))) FROM (SELECT * FROM synthese.bib_protocole) row"
    db.cur.execute(sql)
    protocoles = db.cur.fetchone()[0]

    sql = "SELECT array_to_json(array_agg(row_to_json(row))) FROM (SELECT * FROM utilisateur.bib_structure) row"
    db.cur.execute(sql)
    structures = db.cur.fetchone()[0]


    db.closeAll()
    return render_template('indexDownload.html', protocoles = protocoles, structures = structures, page_title=u"Télécharger des données")



@download.route('/data', methods=['POST'])
def getData():
    db = getConnexion()
    if request.method == 'POST':
        result = request.form
        nom_schema = result['protocole']
        nom_structure = result['structure']

        time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        filename = "Export_"+time
        dirPath = UPLOAD_FOLDER+"/"+filename
        point_path = dirPath+"_point"
        poly_path = dirPath+"_maille"
        point_csv_path = dirPath+"_csv_point.csv"
        poly_csv_path = dirPath+"_csv_maille.csv"
        debug = dirPath+"_debug"
        #construction de la requete a partir du formulaire envoye
        if nom_structure == 'Tous':
            sql_point = "SELECT * FROM "+nom_schema+".layer_point"
        else:
            sql_point = "SELECT * FROM "+nom_schema+".layer_point WHERE nom_structure = '"+nom_structure+"'"
        cmd = """ogr2ogr -f "ESRI Shapefile" """+point_path+""".shp PG:"host="""+database['HOST']+""" user="""+database['USER']+""" dbname="""+database['DATABASE_NAME']+""" password="""+database['PASSWORD']+""" " -sql  """
        cmd = cmd +'"'+sql_point+'"'
        print cmd

        os.system(cmd)

        if nom_structure == 'Tous':
            sql_poly = "SELECT * FROM "+nom_schema+".layer_poly"
        else:    
            sql_poly = "SELECT * FROM "+nom_schema+".layer_poly WHERE nom_structure = '"+nom_structure+"'"
        cmd = """ogr2ogr -f "ESRI Shapefile" """+poly_path+""".shp PG:"host="""+database['HOST']+""" user="""+database['USER']+""" dbname="""+database['DATABASE_NAME']+""" password="""+database['PASSWORD']+""" " -sql  """
        cmd = cmd +'"'+sql_poly+'"'
        os.system(cmd)

        ##CSV
        
        with open(debug, 'w') as file:
            file.write(sql_poly+ "\n")
            file.write(cmd+ "\n")
            file.write(sql_point+ "\n")

        with open(point_csv_path, 'w') as f:
            outputquery = "COPY ({0}) TO STDOUT WITH CSV HEADER DELIMITER AS ';'".format(sql_point)
            db.cur.copy_expert(outputquery, f)
        with open(poly_csv_path, 'w') as f:
            db.outputquery = "COPY ({0}) TO STDOUT WITH CSV HEADER DELIMITER AS ';'".format(sql_poly)
            db.cur.copy_expert(outputquery, f)


        #on zipe le tout
        utils.zipItwithCSV(dirPath, True)

        db.closeAll()
        return send_from_directory(UPLOAD_FOLDER ,filename+".zip")
