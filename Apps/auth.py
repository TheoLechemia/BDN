from functools import wraps
from database import *
from config import config
from flask import redirect, url_for, request, flash, request, session, make_response, abort
import hashlib
import random

from . import utils




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
            print '--------------------------NOUVELLE REQUETE -------------------------------------'
            print ' NOM REQUETE', func.__name__
            if 'user' in session: 
                resp = func(*args, **kwargs)
                token = None
                #si le token existe
                if 'token' in session:
                    print 'LES ANCIEEEEEEEEENS'
                    print 'la session', session['token']
                    print 'le cookie', request.cookies.get('token')
                    ## on check si le token de la session et du header anti XSRF envoye par angular ou du token sont egaux, si oui on regenere un token
                    if session['token'] in (request.headers.get('X-XSRF-TOKEN'), request.cookies.get('token')):
                        print 'le header', request.headers.get('X-XSRF-TOKEN')
                        token = str(random.random())
                        token = hashlib.md5(token).hexdigest()
                        resp.set_cookie('token', token)
                        resp.set_cookie('XSRF-TOKEN', token)
                        resp.set_cookie('auth_level', str(session['auth_level']))
                        session['token'] = token
                        print 'LES NOUVEAUUUUUUUUUUX'
                        print 'la session', session['token']
                        print 'le cookie', request.cookies.get('token')
                        #on check le niveau d authentification
                        if session['auth_level']>=level:
                            return resp
                        else:
                            redirect_resp = make_response(utils.redirect_back(request.referrer))
                            redirect_resp.set_cookie('XSRF-TOKEN', token)
                            resp.set_cookie('token', token)
                            session['token'] = token
                            flash("")
                            return redirect_resp
                    #les tokens ne concorde pas, on revoie a la page de connexion
                    else:
                        print 'LES TOKEN SONT PAS BOOOOOOON'
                        print 'la session', session['token']
                        print 'le cookie', request.cookies.get('token')
                        print 'le header', request.headers.get('X-XSRF-TOKEN')
                        return utils.redirect_back("main.login")
                #il n'a avait pas de token => on redirect
                else:
                    print 'PAS DE TOKEEEEEEEEEEEN'
                    return utils.redirect_back("main.login")
            else:
                print 'PAS DE USER DANS LA SESSIOOOOOOOOOON'
                return utils.redirect_back("main.login")
        return __check_auth
    return _check_auth




