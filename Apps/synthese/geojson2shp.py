
from osgeo import ogr, osr
import os
from ..config import config

def convertUnicodeToString(geometryParam, geomType):
    if geomType == 'point':
        return {'type': 'Point', 'coordinates': geometryParam[u'coordinates']}
    else:
        return {'type': 'MultiPolygon', 'coordinates': geometryParam[u'coordinates']}
    


def export(FileName, geojson, geomType):
    DriverName = "ESRI Shapefile"
    driver = ogr.GetDriverByName(DriverName)
    if os.path.exists(FileName):
        driver.DeleteDataSource(FileName)

    #def of projections
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(4326)

    outSpatialRef = osr.SpatialReference() 
    outSpatialRef.ImportFromEPSG(config['MAP']['PROJECTION'])

    coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
    #create the output shape
    outDataSource = driver.CreateDataSource(FileName)
    if geomType == "point":
        outLayer = outDataSource.CreateLayer(str(FileName), outSpatialRef, geom_type=ogr.wkbPoint)
    else:
        outLayer = outDataSource.CreateLayer(str(FileName), outSpatialRef, geom_type=ogr.wkbMultiPolygon)


    fielListName = ['nom_vern', 'lb_nom', 'cd_nom', 'date', 'protocole', 'observateur', 'structure', 'id_synthese']

    #create the field 
    for f in fielListName:
        field = ogr.FieldDefn(f, ogr.OFTString)
        outLayer.CreateField(field)
    #add the field to the layer


    layerDefinition = outLayer.GetLayerDefn()

    for f in geojson['features']:
        #create a feature
        feature = ogr.Feature(outLayer.GetLayerDefn())
        #fill the fields
        for i in range(layerDefinition.GetFieldCount()):
            newFieldName = layerDefinition.GetFieldDefn(i).GetName()
            oldFieldName = fielListName[i]
            fieldContent = f['properties'][oldFieldName]
            if type(fieldContent) is unicode:
                fieldContent = f['properties'][oldFieldName].encode('utf-8')
                fieldContent = str(fieldContent)
            if type(fieldContent) is list:
                fieldContent = str(fieldContent[0].encode('utf-8'))
            if type(fieldContent) is int:
                fieldContent = str(fieldContent)
            feature.SetField(newFieldName, str(fieldContent))
        #get the geom
        geometry = convertUnicodeToString(f['geometry'], geomType)
        print geometry

        point = ogr.CreateGeometryFromJson(str(geometry))
        print point
        point.Transform(coordTransform) 
        feature.SetGeometry(point)
        #create the feature in the layer
        outLayer.CreateFeature(feature)
        feature.Destroy()