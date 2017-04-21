from flask import Blueprint, render_template, flash, request, redirect, url_for, session
from ..config import config
from ..database import *
import psycopg2
from .. import utils
from ..auth import check_auth, User, loadCurrentUser
import hashlib



main = Blueprint('main', __name__, static_url_path="/main", static_folder="static", template_folder="templates")




@main.route('/login', methods= ['GET','POST'])
def login():
    if request.method == 'POST':
        user_data = request.form
        name = user_data['username']
        inputPassword = user_data['password']
        try:
            currentUser = loadCurrentUser(name)
        except:
            flash("Identifiant ou mot de passe incorrect")
            return redirect(url_for("main.login")) 
        #checke si le pass est correct existe bien
        encode_password = hashlib.md5(inputPassword.encode('utf8')).hexdigest()
        if currentUser.password == encode_password:
            session['user'] = currentUser.username
            session['password'] = encode_password
            session['auth_level'] = currentUser.auth_level
            session['id_structure'] = currentUser.id_structure
            session.permanent = True
            return redirect(url_for("main.index"))
        else:
            flash('Identifiant ou mot de passe incorect')
            return redirect(url_for("main.login"))
    if request.method == 'GET':
        print request.url
        return render_template('login.html')



@main.route('/')
@check_auth(1)
def index():
    db = getConnexion()
    stat = {}
    sql = """WITH nb_taxons AS (SELECT COUNT(DISTINCT cd_nom) as nb_tot_tax FROM synthese.releve),
                  nb_obs AS (SELECT COUNT(*) as nb_tot_obs FROM synthese.releve ),
                  nb_observateur AS (SELECT COUNT(DISTINCT observateur) as nb_tot_observateurs FROM synthese.releve)
            SELECT nb_tot_tax, nb_tot_obs, nb_tot_observateurs
            FROM nb_taxons, nb_obs, nb_observateur """
    db.cur.execute(sql)
    res = db.cur.fetchone()
    stat['nb_tot_tax'] = res[0]
    stat['nb_tot_obs'] = res[1]
    stat['nb_tot_observateurs'] = res[2]
    return render_template('index.html', stat=stat)


@main.route('/deconnexion')
def deconnexion():
    if 'user' in session:
        session.pop('user', None)
        session.pop('password', None)
        session.pop('auth_level', None)
    return redirect(url_for("main.login"))



