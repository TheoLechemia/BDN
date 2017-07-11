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


        for i in range(0,layer.GetFeatureCount()):
            inFeature = layer.GetFeature(i)
            outFeature = ogr.Feature(inLayerDefn)
            for j in range(0, inLayerDefn.GetFieldCount()):
                outFeature.SetField(inLayerDefn.GetFieldDefn(j).GetNameRef(), inFeature.GetField(j))

            outFeature.SetGeometry(geom.Clone())
            outLayer.CreateFeature(outFeature)

    conn.Destroy()
    outDs.Destroy()






