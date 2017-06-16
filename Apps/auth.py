from functools import wraps
from database import *
from config import config
from flask import redirect, url_for, request, flash, request, session, make_response
import hashlib
import random




class User():
    def __init__(self,id, username, password, auth_level, id_structure):
        self.id = id
        self.username = username
        self.password = password
        self.auth_level = auth_level
        self.id_structure = id_structure
    def get_auth_level(self):
        return self.auth_level

    def get_id(self):
        return unicode(self.id)  # python 2

def loadCurrentUser(name):
    db = getConnexion()
    sql = 'SELECT * from utilisateurs.v_userslist_forall_applications WHERE identifiant = %s AND id_application = %s'
    param = [name, config['ID_APPLICATION']]
    db.cur.execute(sql, param)
    u = db.cur.fetchone()
    db.closeAll()
    return User(u[1], u[2], u[6],u[16], u[8])


def check_auth(level):
    def _check_auth(func):
        @wraps(func)
        def __check_auth(*args, **kwargs):
            if 'user' in session: 
                ## on check si le token de la session et du cookie sont egaux, si oui on regenere un token
                resp = func(*args, **kwargs)
                token = None
                if session['token'] == request.cookies.get('token'):
                    token = str(random.random())
                    token = hashlib.md5(token).hexdigest()
                    resp.set_cookie('token', token)
                    print 'AUTH LEVEEEEEEEEEEEL'
                    print session['auth_level']
                    resp.set_cookie('auth_level', str(session['auth_level']))
                    session['token'] = token
                    #on check le niveau d authentification
                    if session['auth_level']>=level:
                        return resp
                    else:
                        redirect_resp = make_response(redirect(request.referrer))
                        redirect_resp.set_cookie('token', token)
                        session['token'] = token
                        flash("")
                        return redirect_resp
                #les tokens ne concorde pas, on revoie a la page de connexion
                else:
                    return redirect(url_for("main.login"))
            else:
                return redirect(url_for("main.login"))
        return __check_auth
    return _check_auth


