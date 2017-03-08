#coding: utf-8
import psycopg2
import csv
from datetime import datetime
from flask import session


from .. import config

#build all the dict
#spec1: abondance, spec2:nombre_exact, spec3:nombre_pied_approximatif, spec4:stade_dev
floreDict = {'spec_1':{
                  1: "5-15",
                  2: "16-25",
                  3: "26-50",
                  4: "51-75",
                  5: "76-100"
                  },
            'spec_3':{
                1: '1-10',
                2: '10-50',
                3: '50-100',
                4: '100-500',
                5: '500-1000',
                6: '>1000'
            },
            'spec_4':{
                1: 'Plantule',
                2: 'Juvénile',
                3: 'Adulte',
                4: 'Bouton',
                5: 'Début de floraison',
                6: 'Pleine floraison',
                7: 'Fin de floraison',
                8: 'Début de fructification',
                9: 'Plein fructification',
                10: 'Fin de fructification',
                11: 'Dissémination',
                12: 'squelette, autre',
                13: 'Ptéridophyte: Prothalle',
                14: 'Ptéridophyte: Sporophyte juvénile',
                15: 'Ptéridophyte: Sporophyte adulte',
                16: 'Ptéridophyte: Sporophyte immature',
                17: 'Ptéridophyte: Sporophyte mature'
            }
}

fauneDict = {'spec_1':{
                12:'Animal mort ou collision',
                1: 'Capture Manuelle',
                13: 'Chant',
                14: 'Cris',
                3: 'Contact Sonore',
                10: 'Contact Visuel',
                2: 'Détection',
                4: 'Empreintes, Traces',
                5: 'Filet',
                6: 'Gîte',
                7: 'Indices (crottes,...)',
                8: 'Nichoir',
                9: 'Nid'
                },
            'spec_2': {
                1: '1-5',
                2: '6-10',
                3: '11-20',
                4: '21-50',
                5: '51-100',
                6: '101-500',
                7: '501-1000',
                8: 'Sup.1000'
            },
            'spec_3':{
                1: 'Alerte',
                2: 'Alimentation',
                3: 'Colonie avec certaines femelles gestantes',
                4: 'Colonie avec jeunes non volants',
                5: 'Colonie avec jeunes volants',
                6: 'Colonie avec males',
                7: 'Colonie avec mis bas',
                8: 'Repos',
                9: 'Colonie de reproduction',
                10: 'Colonie sans jeunes',
                11: 'Comportement parental',
                12: 'Comportement territoirial',
                13: 'Eclosion',
                14: 'Emergence',
                15: 'En chasse',
                16: 'En vol',
                17: 'Estivage',
                18: 'Fuite',
                19: 'Harem',
                20: 'Hibernation',
                21: 'Individus isolés',
                22: 'Léthargie diurne',
                23: 'Léthargie hivernale',
                24: 'Migration',
                25: 'Nidification',
                26: 'Ponte',
                27: 'Reproduction',
                28: 'Transit',
                29: 'Autre',
                30: 'Parade nuptiale'
                },
            'spec_8':{
                1: 'Crotte ou crottier',
                2: 'Ecorçage ou frottis',
                3: 'Empreintes',
                4: 'Epiderme',
                5: 'Guano',
                6: 'Nid',
                7: 'Pelotes de réjection',
                8: 'Restes alimentaires',
                9: "Restes de l'animal",
                10: 'Terrier',
                11: 'Autres',
                12: 'Pelage',
                13: 'Oeufs',
                14: 'Larves',
                15: 'Exuvie'
            }
        }

def getSpec(specNumber, protocole, row):
    stringList = row[specNumber].split('#')
    value = None
    #si le champs n'est pas vide on recupere l'id situe apres le #
    if len(stringList) != 1:
        specInt = int(stringList[1])
        try:
            if protocole == 'FLORE':
                value = floreDict[specNumber][specInt]
            if protocole == 'FAUNE':
                value = fauneDict[specNumber][specInt]
        except KeyError:
            print "Une erreur est survenue, vérifier le tableau de conversion des champs generiques"
    return value

def getSpec_without_dict(specNumber, row):
    tabInter = row[specNumber].split('#')
    value = None
    if len(tabInter) != 1:
        value = tabInter[1]
    return value

def csv2PG(file):
    conn = psycopg2.connect(database=config.DATABASE_NAME, user=config.USER, password=config.PASSWORD, host=config.HOST, port=config.PORT)
    cur = conn.cursor()
    try: 
        with open(file) as csvfile:
            reader = csv.DictReader(csvfile, delimiter = ';', quotechar= '|')
            for row in reader:
                ###COMMUN###
                observateur = row['observateur_nom']+" "+ row['observateur_prenom']
                protocole = row['protocole']
                #on enleve l'heure de la date
                listDate = row['date'].split(' ')
                date = listDate[0]
                dateObject = datetime.strptime(date, "%Y/%M/%d")
                lon = row['loc_x']
                lat = row['loc_y']
                cd_nom = row['taxon_id']
                #formatage en WKT
                point = 'POINT('+lon+' '+lat+')'
                print 'OOOOOOOOOOOOOOOOOOOOOOOOOOH'
                print point
                print dateObject
                valide = "FALSE"
                sql_insee = """ SELECT code_insee FROM layers.commune WHERE ST_INTERSECTS(geom,(ST_Transform(ST_PointFromText(%s, 4326),32620)))"""
                param = [point]
                cur.execute(sql_insee, param)
                resinsee = cur.fetchone()
                insee = None
                if resinsee != None:
                	insee = resinsee[0]

                sql_foret = """ SELECT ccod_frt FROM layers.perimetre_forets WHERE ST_INTERSECTS(geom,(ST_Transform(ST_PointFromText(%s, 4326),32620))) """
                cur.execute(sql_foret, param)
                ccod_frt = None 
                res = cur.fetchone()
                if res != None:
                    ccod_frt = res[0]

                #recupere l'id_structure depuis la session
                id_structure = session['id_structure']




                ###FLORE###
                if protocole == 'FLORE':
                    abondance = getSpec('spec_1', protocole, row)
                    nb_pied = getSpec_without_dict('spec_2', row)
                    nb_pied_approx = getSpec('spec_3', protocole, row)
                    stade_dev = getSpec('spec_4', protocole, row)
                    sql = '''INSERT INTO bdn.flore (protocole, observateur, date, cd_nom, insee, ccod_frt, abondance, nb_pied_approx, nb_pied, stade_dev, geom_point, valide, id_structure, loc_exact)
                           VALUES (%s, %s, %s, %s, %s,%s,%s,%s, %s, %s, ST_Transform(ST_PointFromText(%s, 4326),32620), %s, %s, %s )'''
                    params = [protocole, observateur, dateObject, cd_nom, insee, ccod_frt, abondance, nb_pied_approx, nb_pied, stade_dev, point, valide, id_structure, True]
                    cur.execute(sql, params)
                    conn.commit()

                ###FAUNE###
                if protocole == 'FAUNE':
                    type_obs = getSpec('spec_1', protocole, row)
                    nb_individu_approx = getSpec('spec_2', protocole, row)
                    print nb_individu_approx
                    comportement = getSpec('spec_3', protocole, row)
                    nb_non_identife = getSpec_without_dict('spec_4', row)
                    nb_male = getSpec_without_dict('spec_5', row)
                    nb_femelle = getSpec_without_dict('spec_6', row)
                    nb_jeune = getSpec_without_dict('spec_7', row)
                    trace = getSpec('spec_8', protocole, row)
                    sql = '''INSERT INTO bdn.faune (protocole, observateur, date, cd_nom, insee, ccod_frt, type_obs, nb_individu_approx, comportement, nb_non_identife, nb_male, nb_femelle, nb_jeune, trace, geom_point, valide, id_structure, loc_exact )
                           VALUES (%s, %s, %s, %s, %s,%s,%s, %s, %s, %s, %s, %s, %s, %s, ST_Transform(ST_PointFromText(%s, 4326),32620), %s, %s, %s )'''
                    params = [protocole, observateur, dateObject, cd_nom, insee, ccod_frt, type_obs, nb_individu_approx, comportement, nb_non_identife, nb_male, nb_femelle, nb_jeune, trace, point, valide, id_structure, True]
                    cur.execute(sql, params)
                    conn.commit()

    finally: 
        cur.close()
        conn.close()

