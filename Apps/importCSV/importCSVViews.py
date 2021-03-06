#coding: utf-8
from flask import Flask, request, render_template, url_for, redirect, send_from_directory, flash, session, Blueprint, json, make_response
import csv2postgreSQL_carnet_terrain
import csv2postgreSQL

import csv
from Apps.database import *

from werkzeug.utils import secure_filename
from werkzeug.wrappers import Response 

import os
from ..initApp import app
import sys
from ..auth import check_auth

importCSV = Blueprint('importCSV', __name__, static_url_path="/importCSV", static_folder="static", template_folder="templates")

#limit à 1mo la taille du fichier upload
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

ALLOWED_EXTENSIONS = set(['csv'])
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
UPLOAD_FOLDER = PARENT_DIR+'/static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@importCSV.route('/', methods=['GET', 'POST'])
@check_auth(2)
def indexImport():
    if request.method == 'GET':
        resp = make_response(render_template('importCSV.html', page_title=u"Import des données naturalistes "))
        return resp
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Aucun fichier selectionne') 
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #write in postgres
            file_type = request.form['inputFile']
            trace = str()
            if file_type == 'observnat':
                print 'OBSERVNAAAAAAAAAAAAAAT'
                trace = csv2postgreSQL.csv2PG(UPLOAD_FOLDER+'/'+filename)
            if file_type == "excel": 
                print 'EXCEEEEEEEEEEEEEL'
                trace = csv2postgreSQL_carnet_terrain.csv2PG(UPLOAD_FOLDER+'/'+filename)
            flash(trace)
            return redirect(request.url)
        else:
            flash("Le fichier n'est pas au format .CSV")
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(request.url)

@importCSV.route('/uploads/<filename>')
@check_auth(2)
def uploaded_fileCSV(filename):
    return Response(json.dumps('fichier bien uploade'), mimetype='application/json')
    #return send_from_directory(app.config['UPLOAD_FOLDER'],filename)


@importCSV.route('/error/<customError>')
@check_auth(2)
def handle_custom_error(customError):
        return Response(json.dumps(e), mimetype='application/json')

    