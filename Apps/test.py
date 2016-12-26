import psycopg2
import psycopg2.extras


conn = psycopg2.connect(database="bdn", user="onfuser", password="Martine50=", host="localhost", port="5432")
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


point = "POINT(-61.74450 16.096661)"
sql_insee = """ SELECT code_insee FROM layers.commune WHERE ST_INTERSECTS(geom,(ST_Transform(ST_PointFromText(%s, 4326),32620)))"""
param = [point]
cur.execute(sql_insee, param)
print cur.fetchone()[0]


# what = 212
# sql = """ SELECT ST_AsGeoJSON(ST_TRANSFORM(s.geom_point, 4326)), s.id_synthese, t.lb_nom, t.cd_nom
#               FROM bdn.synthese s
#               JOIN taxonomie.taxref_v10 t ON t.cd_nom = s.cd_nom
#               WHERE s.cd_nom = 212 ;"""
# param = [what]
# print cur.execute(sql)

# # for r in res:
# # 	print r

cur.close()
conn.close()

import os
import zipfile


def zipdir(dirPath=None, zipFilePath=None, includeDirInZip=True):
    """Create a zip archive from a directory.
    
    Note that this function is designed to put files in the zip archive with
    either no parent directory or just one parent directory, so it will trim any
    leading directories in the filesystem paths and not include them inside the
    zip archive paths. This is generally the case when you want to just take a
    directory and make it into a zip file that can be extracted in different
    locations. 
    
    Keyword arguments:
    
    dirPath -- string path to the directory to archive. This is the only
    required argument. It can be absolute or relative, but only one or zero
    leading directories will be included in the zip archive.

    zipFilePath -- string path to the output zip file. This can be an absolute
    or relative path. If the zip file already exists, it will be updated. If
    not, it will be created. If you want to replace it from scratch, delete it
    prior to calling this function. (default is computed as dirPath + ".zip")

    includeDirInZip -- boolean indicating whether the top level directory should
    be included in the archive or omitted. (default True)

"""
    # if not zipFilePath:
    #     zipFilePath = dirPath + ".zip"
    # if not os.path.isdir(dirPath):
    #     raise OSError("dirPath argument must point to a directory. "
    #         "'%s' does not." % dirPath)
    # parentDir, dirToZip = os.path.split(dirPath)
    # #Little nested function to prepare the proper archive path
    # def trimPath(path):
    #     archivePath = path.replace(parentDir, "", 1)
    #     if parentDir:
    #         archivePath = archivePath.replace(os.path.sep, "", 1)
    #     if not includeDirInZip:
    #         archivePath = archivePath.replace(dirToZip + os.path.sep, "", 1)
    #     return os.path.normcase(archivePath)
        
    # outFile = zipfile.ZipFile(zipFilePath, "w",
    #     compression=zipfile.ZIP_DEFLATED)
    # for (archiveDirPath, dirNames, fileNames) in os.walk(dirPath):
    #     for fileName in fileNames:
    #         filePath = os.path.join(archiveDirPath, fileName)
    #         outFile.write(filePath, trimPath(filePath))
    #     #Make sure we get empty directories as well
    #     if not fileNames and not dirNames:
    #         zipInfo = zipfile.ZipInfo(trimPath(archiveDirPath) + "/")
    #         #some web sites suggest doing
    #         #zipInfo.external_attr = 16
    #         #or
    #         #zipInfo.external_attr = 48
    #         #Here to allow for inserting an empty directory.  Still TBD/TODO.
    #         outFile.writestr(zipInfo, "")
    # outFile.close()

dirPath = "C:\Users\\tl90744\\Documents\\observValid_2\\uploads\\2016_12_15_09_14_06_970000"
# zipFilePath = "C:\Users\\tl90744\\Documents\\observValid_2\\uploads"
# zipdir(dirPath,zipFilePath)


# for filename in dirPath:
# 	print filename

zf = zipfile.ZipFile(dirPath+'.zip', mode='w')

for (archiveDirPath, dirNames, fileNames) in os.walk(dirPath):
        for fileName in fileNames:
        	filePath = os.path.join(archiveDirPath, fileName)
        	zf.write(filePath, os.path.basename(filePath))

zf.close()