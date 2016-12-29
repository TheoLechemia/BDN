import config
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
    conn = psycopg2.connect(database=config.DATABASE_NAME, user=config.USER, password=config.PASSWORD, host=config.HOST, port=config.PORT)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    connexion = DatabaseInterface(conn, cur)
    return connexion

