from .config import database
import psycopg2
import psycopg2.extras

class DatabaseInterface:
    conn = None
    cur = None

    def __init__(self, conn, cur):
        self.conn = conn
        self.cur = cur

    def closeAll(self):
        self.conn.close()
        self.cur.close()


def getConnexion():
    conn = psycopg2.connect(database=database['DATABASE_NAME'], user=database['USER'], password=database['PASSWORD'], host=database['HOST'], port=database['PORT'])
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    connexion = DatabaseInterface(conn, cur)
    return connexion

