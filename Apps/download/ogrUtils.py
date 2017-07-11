import ogr
import osr
import os
from ..config import config, database




def pg2shp(table, outputPath, sql=None):
    conn = ogr.Open("PG: host="+database['HOST']+" user="+database['USER']+" dbname="+database['DATABASE_NAME']+" password="+database['PASSWORD'])
    #Remove output shapefile if it already exists
    outDriver = ogr.GetDriverByName('ESRI Shapefile') 
    if os.path.exists(outputPath):
        outDriver.DeleteDataSource(outputPath)

    outDs = outDriver.CreateDataSource(outputPath)
    #is point or maille ?
    tableName = table.split('.')[-1]
    geomType = ogr.wkbPoint if tableName == 'layer_point' else ogr.wkbPolygon
    #rajouter le systeme de projection
    outSpatialRef = osr.SpatialReference() 
    outSpatialRef.ImportFromEPSG(config['MAP']['PROJECTION'])

    outLayer = outDs.CreateLayer(outputPath, outSpatialRef, geomType)

    layer = conn.GetLayerByName(str(table))
    if sql:
        layer = conn.ExecuteSQL(sql)
    print table
    print 'LAYEEEEEEEEEER', layer
    firstFeature = layer.GetNextFeature()
    #si la layer contient au moins une ligne
    if firstFeature:
        #recupere le nom des champs et les cree dans le shape en sortie
        for i in range(0, firstFeature.GetFieldCount()):
            fieldDef = firstFeature.GetDefnRef().GetFieldDefn(i)
            outLayer.CreateField(fieldDef)
            geom = firstFeature.GetGeometryRef()

        #reset cursor
        layer.ResetReading()

        outLayerDefn = outLayer.GetLayerDefn()

        inLayer = conn.GetLayer()
        for inFeature in inLayer:
            #create a feature in output
            outFeature = ogr.Feature(outLayerDefn)
            # loop over fields of each feature
            print outFeature.GetFieldCount()
            for i in range(0, outFeature.GetFieldCount()):
                #all regular fields
                outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(),inFeature.GetField(i))
                #geom field
                geom = inFeature.GetGeometryRef()
            outFeature.SetGeometry(geom.Clone())
            outLayer.CreateFeature(outFeature)

    conn.Destroy()
    outDs.Destroy()





