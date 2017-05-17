import flask
from ..database import *
from .. import utils
from ..config import config
from ..auth import check_auth
from werkzeug.wrappers import Response 


meta = flask.Blueprint('meta', __name__, static_url_path="/meta", static_folder="static", template_folder="templates")


@meta.route("/")
@check_auth(3)
def meta_index():
    return flask.render_template('metaIndex.html', configuration=config, page_title=u"Gestion des projets de la BDN")

@meta.route("/listProject", methods=['GET'])
@check_auth(3)
def getProjects():
    db = getConnexion()
    sql = 'SELECT * FROM synthese.bib_projet'
    res = utils.sqltoDict(sql, db.cur)
    db.closeAll()
    return  Response(flask.json.dumps(res), mimetype='application/json')

#recupere le projet et le formulaire de sasisie si il existe
@meta.route("/getProject/<idproject>", methods=['GET'])
@check_auth(3)
def getOneProject(idproject):
    db = getConnexion()
    sql = 'SELECT * FROM synthese.bib_projet WHERE id_projet ='+idproject
    res = utils.sqltoDict(sql, db.cur)
    formulaire = None
    if res[0]['saisie_possible']:
        sql = "SELECT * from "+res[0]['bib_champs']
        formulaire = utils.sqltoDict(sql, db.cur)
    db.closeAll()
    return  Response(flask.json.dumps({'projet':res[0], 'formulaire': formulaire}), mimetype='application/json')


@meta.route("/editProject", methods=['POST'])
@check_auth(3)
def editProject():
    if flask.request.method == 'POST':
        db = getConnexion()
        projectForm = flask.request.json['projectForm']
        fieldForm = flask.request.json['fieldForm']
        nbNewField = flask.request.json['nbNewField']

        bib_champs = projectForm['bib_champs']
        nom_schema = projectForm['nom_schema']
        fullTableName = nom_schema+".releve"
        #UPDATE table bib_projet
        sql = """UPDATE synthese.bib_projet
                 SET service_onf = %s, partenaires = %s, subvention_commande = %s, duree = %s, initiateur = %s, commentaire = %s"""
        params = [projectForm['service_onf'], projectForm['partenaires'], projectForm['subvention_commande'], projectForm['duree'], projectForm['initiateur'], projectForm['commentaire']]
        db.cur.execute(sql, params)
        db.conn.commit()

        # si le projet a une table independanta on modifie sa table bib_champ et sa table releve
        if projectForm['table_independante']: 
            delete = "DELETE FROM "+bib_champs
            db.cur.execute(delete)
            db.conn.commit()
            for r in fieldForm:
                #modif dans bib_champs
                sql = "INSERT INTO """+bib_champs+" VALUES(%s, %s, %s, %s, %s, %s, %s)"
                params = [r['id_champ'], r['no_spec'], r['nom_champ'], r['valeur'], r['lib_champ'], r['type_widget'], r['db_type']]
                db.cur.execute(sql, params)
                #modif dans la table releve
                sql = "ALTER TABLE "+fullTableName+" ADD COLUMN "+r['nom_champ']
                db.conn.commit()
            #ajout des nouveaux champs dans la table releve
            #on split le tab pour avoir que les nouveaux champs
            newFields = fieldForm[nbNewField * -1:]
            for f in newFields:
                sql = "ALTER TABLE "+fullTableName+" ADD COLUMN "+f['nom_champ']+" "+f['db_type']
                db.cur.execute(sql, params)
                db.conn.commit()
            #change le template HTML

            utils.createTemplate(nom_schema, fieldForm)

        db.closeAll()
    

    return  Response(flask.json.dumps('res'), mimetype='application/json')


@meta.route("/addProject", methods=['POST'])
@check_auth(3)
def addProject():
    if flask.request.method == 'POST':
        db = getConnexion()
        projectForm = flask.request.json['projectForm']
        fieldForm = flask.request.json['fieldForm']
        table_indep = projectForm['table_independante']
        nom_schema = str()
        if table_indep == "False":
            saisie_possible = False
            nom_schema = 'synthese'
            nom_table = 'releve'
            template = None
            bib_champs = None
        else:
            saisie_possible = True
            nom_schema = projectForm['nom_bdd']
            nom_table = 'releve'
            template = 'addObs/'+nom_schema+'.html'
            bib_champs = nom_schema+'.'+'bib_champs_'+nom_schema
            utils.createProject(db, projectForm,fieldForm)

        #insert dans bib_projet
        sql = """INSERT INTO synthese.bib_projet(nom_projet, theme_principal, service_onf, partenaires,subvention_commande, duree, initiateur, commentaire, table_independante, saisie_possible, nom_schema, nom_table, template, bib_champs ) 
              VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        params = [projectForm['nom_projet'], projectForm['theme_principal'], projectForm['service'], projectForm['partenaires'], projectForm['subvention_commande'], projectForm['duree'], projectForm['initiateur'], projectForm['commentaire'], projectForm['table_independante'],\
                 saisie_possible, nom_schema, nom_table, template, bib_champs ]
        db.cur.execute(sql, params)
        db.conn.commit()
        #update le template de saisie
        print 'UPDATEEEEEEEE template'
        utils.createTemplate(nom_schema, fieldForm)
        print 'ENDDDDDDDDDDDDDDD UPDATEEEEEEEE template'
        db.closeAll()

        return  Response(flask.json.dumps('success'), mimetype='application/json')