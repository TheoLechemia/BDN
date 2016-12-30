#coding: utf-8
from flask import Flask, request, render_template, url_for, redirect, send_from_directory, flash, session, Blueprint
import csv2postgreSQL

from werkzeug.utils import secure_filename
import os
from ..initApp import app

importCSV = Blueprint('importCSV', __name__)




CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

ALLOWED_EXTENSIONS = set(['csv'])
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
UPLOAD_FOLDER = PARENT_DIR+'/static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'Martine50='  # Change this!


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@importCSV.route('/', methods=['GET', 'POST'])
def indexImport():
    if request.method == 'GET':
        return render_template('importCSV.html', page_title=u"Import des données naturalistes ")
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            #flash('Aucun fichier selectionne') 
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #write in postgres
            csv2postgreSQL.csv2PG(UPLOAD_FOLDER+'/'+filename)
            flash('Fichier ajoute avec succes')
            return redirect(request.url)
            #return redirect(url_for('importCSV.uploaded_fileCSV', filename=filename))
        else:
            flash("Le fichier n'est pas au format .CSV")
            return redirect(request.url)

@importCSV.route('/uploads/<filename>')
def uploaded_fileCSV(filename):
    return 'fichier bien uploade'
    #return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

    