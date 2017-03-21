# coding: utf-8
from flask import Flask, request, render_template, url_for, redirect, send_from_directory, flash, session, Blueprint, json, Response

from ..auth import check_auth

from ..config import database
from ..database import *

from .. import utils

from datetime import datetime
import os


download = Blueprint('download', __name__, static_url_path="/download", static_folder="static", template_folder="templates")
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
UPLOAD_FOLDER = PARENT_DIR+'\\static\\uploads'

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
    if request.method == 'POST':
        result = request.form
        nom_schema = result['protocole']
        id_structure = result['structure']

        time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        filename = "Export_"+time
        dirPath = UPLOAD_FOLDER+"\\"+filename
        point_path = dirPath+"_point"
        poly_path = dirPath+"_maille"
        #construction de la requete a partir du formulaire envoye
        if id_structure == 'Tout':
            sql = "SELECT * FROM "+nom_schema+".layer_point"
        else:
            sql = "SELECT * FROM "+nom_schema+".layer_point"
        sql = """SELECT * FROM """+nom_schema+""".layer_point WHERE id_structure = """+id_structure
        cmd = """ogr2ogr -f "ESRI Shapefile" """+point_path+""".shp PG:"host="""+database['HOST']+""" user="""+database['USER']+""" dbname="""+database['DATABASE_NAME']+""" password="""+database['PASSWORD']+""" " -sql  """
        cmd = cmd +'"'+sql+'"'
        print cmd
        # output = open(UPLOAD_FOLDER+"\\truc.txt", "w")
        # output.write(cmd)
        #output.close()
        #cree un dossier avec les shapefiles dedans (shp, shx etc..)
        os.system(cmd)
        if id_structure == 'Tout':
            sql = "SELECT * FROM "+nom_schema+".layer_poly"
        else:    
            sql = """SELECT * FROM """+nom_schema+""".layer_poly WHERE id_structure = """+id_structure
        cmd = """ogr2ogr -f "ESRI Shapefile" """+poly_path+""".shp PG:"host="""+database['HOST']+""" user="""+database['USER']+""" dbname="""+database['DATABASE_NAME']+""" password="""+database['PASSWORD']+""" " -sql  """
        cmd = cmd +'"'+sql+'"'
        os.system(cmd)
        #on zipe le tout
        utils.zipIt(dirPath, True)
        print UPLOAD_FOLDER
        print filename
        return send_from_directory(UPLOAD_FOLDER ,filename+".zip")
        #return Response(json.dumps(nom_schema), mimetype='application/json')