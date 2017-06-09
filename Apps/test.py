import psycopg2
import psycopg2.extras
import os
from database import *


# APP_DIR = os.path.abspath(os.path.dirname(__file__))

# htmlFileName = APP_DIR+"/addObs/static/test.html"
# htmlFile = open(htmlFileName, "w")


db=getConnexion()
for i in range(5000):
	db.cur.execute("""INSERT INTO synthese.releve (observateur, date,geom_point, cd_nom, valide, diffusable, id_projet, loc_exact)
	VALUES('test', '1900-01-01', '01010000206C7F000000000000E492234100000000570D3B41', 212, TRUE, TRUE, 61, TRUE)""")
	db.conn.commit()
db.closeAll()
