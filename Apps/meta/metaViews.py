import flask
from ..database import *
from .. import utils
from ..config import config
from ..auth import check_auth
from werkzeug.wrappers import Response 
from psycopg2 import sql as psysql


meta = flask.Blueprint('meta', __name__, static_url_path="/meta", static_folder="static", template_folder="templates")


@meta.route("/")
@check_auth(3)
def meta_index():
    resp = flask.make_response(flask.render_template('metaIndex.html', configuration=config, page_title=u"Gestion des projets de la BDN"))
    return resp

@meta.route("/listProject", methods=['GET'])
@check_auth(3)
def getProjectsList():
    db = getConnexion()
    sql = 'SELECT * FROM synthese.bib_projet ORDER BY id_projet DESC'
    res = utils.sqltoDict(sql, db.cur)
    db.closeAll()
    return  Response(flask.json.dumps(res), mimetype='application/json')

#recupere le projet et le formulaire de sasisie si il existe
@meta.route("/getProject/<idproject>", methods=['GET'])
@check_auth(3)
def getOneProject(idproject):
    db = getConnexion()
    sql = 'SELECT * FROM synthese.bib_projet WHERE id_projet = %s'
    res = utils.sqltoDictWithParams(sql,[idproject], db.cur)
    formulaire = None
    if res[0]['table_independante']:
        bib_champs = res[0]['bib_champs']
        schema_name = bib_champs.split('.')[0]
        table_name = bib_champs.split('.')[1]
        sql = "SELECT * from {sch}.{tbl}"
        formatedSql = psysql.SQL(sql).format(sch=psysql.Identifier(schema_name), tbl=psysql.Identifier(table_name)).as_string(db.cur)

        formulaire = utils.sqltoDict(formatedSql, db.cur)
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

        bib_champs = projectForm['nom_bdd']+'.bib_champs_'+projectForm['nom_bdd']
        projet_nom_schema = projectForm['nom_schema']
        fullTableName = projet_nom_schema+".releve"
        template = 'addObs/'+projet_nom_schema+'.html'
        if utils.checkForInjection(projet_nom_schema):
            return Response(flask.json.dumps("Tu crois que tu vas m'injecter ??"), mimetype='application/json')
        else:
            #UPDATE table bib_projet
            update = """UPDATE synthese.bib_projet
                     SET service_onf = %s, partenaires = %s, subvention_commande = %s, duree = %s, initiateur = %s, producteur = %s, commentaire = %s, template = %s
                     WHERE id_projet = %s"""
                        
            params = [projectForm['service_onf'], projectForm['partenaires'], projectForm['subvention_commande'], projectForm['duree'], projectForm['initiateur'], projectForm['producteur'], projectForm['commentaire'], template, projectForm['id_projet']  ]
            db.cur.execute(update, params)
            db.conn.commit()

            # si le projet a une table independanta on modifie sa table bib_champ et sa table releve

            if projectForm['table_independante']: 
                schema_name = bib_champs.split('.')[0]
                table_name = bib_champs.split('.')[1]
                delete = "DELETE FROM {sch}.{tbl}"
                delete = psysql.SQL(delete).format(sch=psysql.Identifier(schema_name), tbl=psysql.Identifier(table_name)).as_string(db.cur)
                db.cur.execute(delete)
                db.conn.commit()
                for r in fieldForm:
                    #modif dans bib_champs
                    query = "INSERT INTO {sch}.{tbl} VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
                    query = psysql.SQL(query).format(sch=psysql.Identifier(schema_name), tbl=psysql.Identifier(table_name)).as_string(db.cur)

                    params = [r['id_champ'], r['no_spec'], r['nom_champ'], r['valeur'], r['lib_champ'], r['type_widget'], r['db_type'], r['obligatoire']]
                    db.cur.execute(query, params)
                    db.conn.commit()
                #ajout des nouveaux champs dans la table releve
                #on split le tab pour avoir que les nouveaux champs
                if nbNewField != 0:
                    newFields = fieldForm[nbNewField * -1:]
                    for f in newFields:
                        query= "ALTER TABLE {sch}.{tbl} ADD COLUMN {col} {type}"
                        query = psysql.SQL(query).format(sch=psysql.Identifier(schema_name), tbl=psysql.Identifier('releve'), col=psysql.Identifier(f['nom_champ']), type=psysql.Literal(f['db_type'])).as_string(db.cur)
                        #hack pour enlever les simple quote
                        query = query.replace("'","")
                        db.cur.execute(query)
                        db.conn.commit()
                #change le template HTML
            deleteView = """DROP VIEW IF EXISTS {tbl}.to_csv;
                            DROP VIEW IF EXISTS {tbl}.layer_poly;
                            DROP VIEW IF EXISTS {tbl}.layer_point;"""
            deleteView = psysql.SQL(deleteView).format(tbl=psysql.Identifier(schema_name)).as_string(db.cur)
            print deleteView
            db.cur.execute(deleteView)
            db.conn.commit()
            utils.createViewsDownload(db, projectForm, fieldForm)
            utils.createTemplate(schema_name, fieldForm)

            db.closeAll()
        return  Response(flask.json.dumps('res'), mimetype='application/json')


@meta.route("/addProject", methods=['POST'])
@check_auth(3)
def addProject():
    if flask.request.method == 'POST':
        db = getConnexion()
        projectForm = flask.request.json['projectForm']
        fieldForm = flask.request.json['fieldForm']
        template = str()
        nom_schema = str()
        if not projectForm['table_independante']:
            nom_schema = 'synthese'
            nom_table = 'releve'
            template = None
            bib_champs = None
        else:
            saisie_possible = True
            nom_table = 'releve'
            nom_schema = projectForm['nom_bdd']
            bib_champs = nom_schema+'.'+'bib_champs_'+nom_schema
            #creation du schema + table + triggers
            utils.createProject(db, projectForm, fieldForm)
            #creation des vues pour le download
            utils.createViewsDownload(db, projectForm, fieldForm)
            template = 'addObs/'+nom_schema+'.html'
            utils.createTemplate(nom_schema, fieldForm)
        if projectForm['saisie_possible']:
            utils.create_taxonomie_view(db, projectForm, fieldForm)

        #insert dans bib_projet
        sql = """INSERT INTO synthese.bib_projet(nom_projet, theme_principal, service_onf, partenaires,subvention_commande, duree, initiateur, producteur, commentaire, table_independante, saisie_possible, nom_schema, nom_table, template, bib_champs, nom_bdd ) 
              VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)"""
        params = [projectForm['nom_projet'], projectForm['theme_principal'], projectForm['service'], projectForm['partenaires'], projectForm['subvention_commande'], projectForm['duree'], projectForm['initiateur'], projectForm['producteur'], projectForm['commentaire'], projectForm['table_independante'],\
                 projectForm['saisie_possible'], nom_schema, nom_table, template, bib_champs, nom_schema ]
        db.cur.execute(sql, params)
        db.conn.commit()
        db.closeAll()

        return  Response(flask.json.dumps('success'), mimetype='application/json')