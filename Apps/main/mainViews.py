#coding: utf-8
from flask import Blueprint, render_template, flash, request, redirect, url_for, session, make_response, json, abort
from ..config import config
from ..database import *
import psycopg2
from .. import utils
from ..auth import check_auth, User, loadCurrentUser
import hashlib
import time
import random
from werkzeug.wrappers import Response 





main = Blueprint('main', __name__, static_url_path="/main", static_folder="static", template_folder="templates")





@main.route('/login', methods= ['GET','POST'])
def login():
    if request.method == 'GET':
        csrf_token = str(random.randrange(16**30))
        session['csrf_token'] = csrf_token
        return render_template('login.html',csrf_token=csrf_token)

    if request.method == 'POST':
        #csrf check
        token = session.pop('csrf_token', None)
        print str(token) != str(request.form.get('csrf_token'))
        if not token or token != request.form.get('csrf_token'):
            abort(403)
        db = getConnexion()
        #IP du visiteur:
        ip_visitor = request.remote_addr
        query = "SELECT * FROM ip_connexion WHERE ip = %s"
        db.cur.execute(query, [ip_visitor])
        res = db.cur.fetchall()
        #si cette ip c'est a echoue trop de fois, elle ne peux plus reesayer de se connecter
        if len(res)>= 5:
            flash("Vous avez échoué trop de fois, réssayer demain !")
            return utils.redirect_back("main.login")
            #return redirect(url_for("main.login"))
        else:
            user_data = request.form
            name = user_data['username']
            inputPassword = user_data['password']
            #latence pour eviter les attaques, augmente a chaque fois
            time.sleep(len(res))
            try:
                currentUser = loadCurrentUser(name)
            except:
                flash("Identifiant ou mot de passe incorrect")
                #return redirect(url_for("main.login"))
                return utils.redirect_back("main.login")
            #checke si le pass est correct
            encode_password = hashlib.md5(inputPassword.encode('utf8')).hexdigest()
            #si le mdp est OK
            if currentUser.password == encode_password:
                session['user'] = currentUser.username
                session['auth_level'] = currentUser.auth_level
                session['id_structure'] = currentUser.id_structure
                #ticket dans la session et le cookie
                token = str(random.random())
                token = hashlib.md5(token).hexdigest()
                #test = my_self_url(request.form['next'])
                #resp = make_response(redirect(url_for("main.index")))
                resp = make_response(utils.redirect_back("main.index"))
                resp.set_cookie('token', token)
                session['token'] = token
                return resp
            # si le mdp est pas bon, on enregistre l'ip
            else:
                flash('Identifiant ou mot de passe incorect')
                query = "INSERT INTO ip_connexion (ip) VALUES(%s)"
                db.cur.execute(query, [ip_visitor])
                db.conn.commit()
                return utils.redirect_back("main.login")
                #return redirect(url_for("main.login"))



@main.route('/')
@check_auth(1)
def index():
    resp = make_response(render_template('index.html', configuration=config))
    return resp

@main.route('/getStats', methods=['GET'])
@check_auth(1)
def getStat():
    db = getConnexion()
    stat = dict()
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
    db.closeAll()
    return Response(json.dumps(stat), mimetype='application/json')

@main.route('/getAllTaxons', methods=['GET'])
@check_auth(1)
def getAllTaxons():
    db = getConnexion()
    sql = """SELECT DISTINCT s.cd_nom, count(s.cd_nom), lb_nom, nom_vern
            FROM synthese.releve s
            JOIN taxonomie.taxref t ON s.cd_nom = t.cd_nom
            GROUP BY s.cd_nom, lb_nom, nom_vern """
    db.cur.execute(sql)
    res = db.cur.fetchall()
    listTaxons = list()
    for r in res:
        inter = {'cd_nom': r[0], 'nb':r[1], 'lb_nom':r[2], 'nom_vern': r[3]}
        listTaxons.append(inter)
    return Response(json.dumps(listTaxons), mimetype='application/json')



@main.route('/deconnexion')
@check_auth(1)
def deconnexion():
    #clear la session redirige automatiquement vers la page d'accueil avec check_auth
    if 'user' in session:
        session.clear()
    return Response(json.dumps('deconnexion'), mimetype='application/json') 



