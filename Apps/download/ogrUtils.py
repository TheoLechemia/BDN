import ogr
import osr
import os
from ..config import config, database
import sys




def pg2shp(table, outputPath, sql=None):
    '''Fonction qui converti en shape une
     table postgis en fontion d une requete SQL
     '''
    conn = ogr.Open("PG: host="+database['HOST']+" user="+database['USER']+" dbname="+database['DATABASE_NAME']+" password="+database['PASSWORD'])
    #Remove output shapefile if it already exists
    outDriver = ogr.GetDriverByName('ESRI Shapefile') 
    if os.path.exists(outputPath):
        outDriver.DeleteDataSource(outputPath)

    outDs = outDriver.CreateDataSource(outputPath)
    #is point or maille ?
    tableName = table.split('.')[-1]
    geomType = ogr.wkbPoint if tableName == 'layer_point' else ogr.wkbPolygon
    #rajoute le systeme de projection
    outSpatialRef = osr.SpatialReference() 
    outSpatialRef.ImportFromEPSG(config['MAP']['PROJECTION'])

    outLayer = outDs.CreateLayer(outputPath, outSpatialRef, geomType)

    layer = conn.GetLayerByName(str(table))
    if sql:
        layer = conn.ExecuteSQL(sql)
    firstFeature = layer.GetNextFeature()
    #si la layer contient au moins une ligne
    if firstFeature:
        #recupere le nom des champs et les cree dans le shape en sortie
        fields = list()
        for i in range(0, firstFeature.GetFieldCount()):
            fieldDef = firstFeature.GetDefnRef().GetFieldDefn(i)
            fields.append(fieldDef.GetName())
            outLayer.CreateField(fieldDef)


        outLayerDefn = outLayer.GetLayerDefn()
        inLayerDefn = layer.GetLayerDefn()


        layer.ResetReading()

        print 'NB featureeeee', layer.GetFeatureCount()

        for i in range(0,layer.GetFeatureCount()):
            inFeature = layer.GetFeature(i)
            for j in range(0, inLayerDefn.GetFieldCount()):
                print >> sys.stderr, 'INNNNNNNNNNN',inLayerDefn.GetFieldDefn(j).GetNameRef()
                print >> sys.stderr, 'OUTTTTTTTTTTTT', outLayerDefn.GetFieldDefn(j).GetNameRef()
                indexIn = inFeature.GetFieldIndex(inLayerDefn.GetFieldDefn(j).GetNameRef())
                indexOut = inFeature.GetFieldIndex(outLayerDefn.GetFieldDefn(j).GetNameRef())
                print >> sys.stderr, 'INDEX INNNNN', indexIn 
                print >> sys.stderr, "INDEX OUTTTTTTTT", indexOut 

        # for i in range(0,layer.GetFeatureCount()):
        #     inFeature = layer.GetFeature(i)
        #     #create a feature in output
        #     outFeature = ogr.Feature(outLayerDefn)
        #     # loop over fields of each feature
        #     for i in range(0, outLayerDefn.GetFieldCount()):
        #         #all regular fields
        #         print >> sys.stderr, "DEBUUUUUUUUUUUUUUUUUUUUUUUUUG"
        #         print >> sys.stderr, inLayerDefn.GetFieldDefn(i).GetNameRef()
        #         #print >> sys.stderr, inFeature.GetField(i)
        #         index = inFeature.GetFieldIndex(inLayerDefn.GetFieldDefn(i).GetNameRef())
        #         #print >> sys.stderr, index
        #         if index != -1:
        #             print >> sys.stderr, inFeature.GetField(index)
        #         else:
        #             print >> sys.stderr, inLayerDefn.GetFieldDefn(i).GetNameRef()
        #         #outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(),inFeature.GetField(index))
        #     #geom field
        #     geom = inFeature.GetGeometryRef()
        #     outFeature.SetGeometry(geom.Clone())
        #     outLayer.CreateFeature(outFeature)

    conn.Destroy()
    outDs.Destroy()





