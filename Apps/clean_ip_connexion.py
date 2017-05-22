#coding: utf-8

from . import database

db.getConnexion()
db.cur.execute('DELETE FROM ip_connexion')
db.conn.commit()
db.closeAll()