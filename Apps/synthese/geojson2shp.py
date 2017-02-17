
from osgeo import ogr, osr
import os

def convertUnicodeToString(geometryParam):
	 return {'type': 'Point', 'coordinates': geometryParam[u'coordinates']}
	


def export(FileName, geojson):
	DriverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(DriverName)
	if os.path.exists(FileName):
		driver.DeleteDataSource(FileName)

	#def of projections
	inSpatialRef = osr.SpatialReference()
	inSpatialRef.ImportFromEPSG(4326)

	outSpatialRef = osr.SpatialReference() 
	outSpatialRef.ImportFromEPSG(32620)

	coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

	#create the output shape
	outDataSource = driver.CreateDataSource(FileName)
	outLayer = outDataSource.CreateLayer(str(FileName), outSpatialRef, geom_type=ogr.wkbPoint)

	#build the fieldList from the 'propertie' dict of the geojson
	fielListName = list()
	for key in geojson['features'][0]['properties']:
		fielListName.append(str(key))

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
			if fieldContent is unicode:
				fieldContent = f['properties'][oldFieldName].encode('utf-8')
				fieldContent = str(fieldContent)
			if type(fieldContent) is list:
				fieldContent = str(fieldContent[0].encode('utf-8'))
			feature.SetField(newFieldName, fieldContent)
		#get the geom
		geometry = convertUnicodeToString(f['geometry'])

		point = ogr.CreateGeometryFromJson(str(geometry))
		point.Transform(coordTransform) 
		feature.SetGeometry(point)
		#create the feature in the layer
		outLayer.CreateFeature(feature)
		feature.Destroy()