#coding: utf-8

from database import getConnexion

db = getConnexion()
db.cur.execute('DELETE FROM ip_connexion;')
db.conn.commit()
db.closeAll()