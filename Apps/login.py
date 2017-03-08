from initApp import login_manager
from . import config
from . import database
from flask.ext.login import UserMixin




class User(UserMixin):
    def __init__(self,id, username, password, auth_level):
        self.id = id
        self.username = username
        self.password = password
        self.auth_level = auth_level
    def get_auth_level(self):
        return self.auth_level

    




@login_manager.user_loader
def load_user(myid):
     db = getConnexion()
     sql = 'SELECT * from utilisateur.login WHERE nom = %s'
     param = [myid] 
     db.cur.execute(sql, param)
     u = db.cur.fetchone()[0]
     
    return User(u.id, u.name,u.password,u.auth_level)


# def login_required(auth_level):
#     def wrapper(fn):
#         @wraps(fn)
#         def decorated_view(*args, **kwargs):

#             if not current_user.is_authenticated():
#                return current_app.login_manager.unauthorized()
#             urole = current_app.login_manager.reload_user().get_urole()
#             if ( (urole != role) and (role != "ANY")):
#                 return current_app.login_manager.unauthorized()      
#             return fn(*args, **kwargs)
#         return decorated_view
#     return wrapper