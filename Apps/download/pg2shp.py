import ogr2ogr
import ogr
import os

conn = ogr.Open("PG: host=127.0.0.1 user=onfuser dbname=bdn password=Martine50=")

sql = "select * from contact_flore.releve"

#output path
path = './test.shp'

#Remove output shapefile if it already exists
outDriver = ogr.GetDriverByName( 'ESRI Shapefile' ) 
if os.path.exists(path):
    outDriver.DeleteDataSource(path)

outDs = outDriver.CreateDataSource(path)
outSrs = None
outLayer = outDs.CreateLayer("point", outSrs, ogr.wkbPoint)
fd = ogr.FieldDefn('name',ogr.OFTString)


layer = conn.GetLayerByName("contact_flore.layer_point")
#layer = conn.ExecuteSQL(sql)


firstFeature = layer.GetNextFeature()
#recupere le nom des champs et les cree dans le shape en sortie
fields = list()
for i in range(0, firstFeature.GetFieldCount()):
    fieldDef = firstFeature.GetDefnRef().GetFieldDefn(i)
    fieldName = fieldDef.GetName()
    fields.append(fieldName)
    outLayer.CreateField(fieldDef)
    geom = firstFeature.GetGeometryRef()


outLayerDefn = outLayer.GetLayerDefn()
inLayerDefn = layer.GetLayerDefn()


inLayer = conn.GetLayer()
for inFeature in inLayer:
    #create a feature in output
    outFeature = ogr.Feature(outLayerDefn)
    # loop over fields of each feature
    for i in range(0, len(fields)):
        #all regular fields
        outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(),inFeature.GetField(i))
        #geom field
        geom = inFeature.GetGeometryRef()
    outFeature.SetGeometry(geom.Clone())
    outLayer.CreateFeature(outFeature)

conn.Destroy()
outDs.Destroy()


print fields

