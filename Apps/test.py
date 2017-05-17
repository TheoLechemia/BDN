import psycopg2
import psycopg2.extras
import os


APP_DIR = os.path.abspath(os.path.dirname(__file__))

htmlFileName = APP_DIR+"/addObs/static/test.html"
htmlFile = open(htmlFileName, "w")

