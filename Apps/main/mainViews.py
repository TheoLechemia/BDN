from flask import Blueprint, render_template, flash, request, redirect, url_for, session
from .. import config
from ..database import *
import psycopg2
from .. import utils



main = Blueprint('main', __name__, static_url_path="/main", static_folder="static", template_folder="templates")


# from ..initApp import login_manager
from .. import config
from .. import database
from flask.ext.login import UserMixin, login_required, login_user, logout_user
from functools import wraps




class User(UserMixin):
    def __init__(self,id, username, password, auth_level):
        self.id = id
        self.username = username
        self.password = password
        self.auth_level = auth_level
    def get_auth_level(self):
        return self.auth_level

    def get_id(self):
        return unicode(self.id)  # python 2

def loadCurrentUser(name):
    db = getConnexion()
    sql = 'SELECT * from utilisateur.login WHERE nom = %s'
    param = [name]
    db.cur.execute(sql, param)
    u = db.cur.fetchone()
    db.closeAll()
    return User(u[0], u[1],u[2],u[3])


def check_auth(level):
    def _check_auth(func):
        @wraps(func)
        def __check_auth(*args, **kwargs):
            if 'user' in session:
                if session['auth_level']>level:
                    return func(*args, **kwargs)
                #else flasher qu'on a pas suffisammen de droit
            else:
                return redirect(url_for("main.login"))
        return __check_auth
    return _check_auth



@main.route('/login', methods= ['GET','POST'])
def login():
    if request.method == 'POST':
        user_data = request.form
        name = user_data['username']
        inputPassword = user_data['password']
        currentUser = loadCurrentUser(name)
        session['user'] = currentUser.username
        session['password'] = currentUser.password
        session['auth_level']= currentUser.auth_level
        session.permanent = True
        #checke si le nom existe bien
        if currentUser.password == inputPassword:
            return redirect(url_for("main.index"))
        else:
            flash('Identifiant ou mot de passe incorect')
            return redirect(url_for("main.login"))
    if request.method == 'GET':
        print request.url
        return render_template('login.html')



@main.route('/')
@check_auth(0)
def index():
    db = getConnexion()
    stat = {}
    sql = """WITH nb_taxons AS (SELECT COUNT(DISTINCT cd_nom) as nb_tot_tax FROM bdn.synthese),
                  nb_obs AS (SELECT COUNT(*) as nb_tot_obs FROM bdn.synthese ),
                  nb_observateur AS (SELECT COUNT(DISTINCT observateur) as nb_tot_observateurs FROM bdn.synthese)
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
    


