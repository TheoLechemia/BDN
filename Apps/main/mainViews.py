from flask import Blueprint, render_template
from .. import config
from ..database import *
import psycopg2
from .. import utils


main = Blueprint('main', __name__, static_url_path="/main", static_folder="static", template_folder="templates")


@main.route('/')
def index():
	db = getConnexion()
	stat = {}
	sql = """WITH nb_taxons AS (SELECT COUNT(DISTINCT cd_nom) as nb_tot_tax FROM bdn.synthese),
     			  nb_obs AS (SELECT COUNT(*) as nb_tot_obs FROM bdn.synthese ),
     			  nb_observateur AS (SELECT COUNT(DISTINCT observateur) as nb_tot_observateurs FROM bdn.synthese)
			SELECT nb_tot_tax, nb_tot_obs, nb_tot_observateurs
			FROM nb_taxons, nb_obs, nb_observateur """
	db.cur.execute(sql)
	res = db.cur.fetchone()
	stat['nb_tot_tax'] = res[0]
	stat['nb_tot_obs'] = res[1]
	stat['nb_tot_observateurs'] = res[2]
	return render_template('index.html', stat=stat)