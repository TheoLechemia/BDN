from functools import wraps
from flask import session, make_response
from database import *
from config import config
from flask import redirect, url_for, request, flash, request




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
                if session['auth_level']>=level:
                    return func(*args, **kwargs)
                else:
                    flash("")
                    print request.referrer
                    return redirect(request.referrer)
            else:
                return redirect(url_for("main.login"))
        return __check_auth
    return _check_auth