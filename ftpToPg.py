#coding: utf-8

import os
from shutil import copyfile
from BDN.apps.importCSV.csv2postgreSQL import csv2PG

for path,dirs,files in os.walk('./depot_terrain/Observatory'):
    for filename in files:
        file_path = os.path.join(path,filename)
        print file_path
        #try to write in PG and copy the csv_file in the save folder
        try:
            #csv2PG(file_path)
            copyfile(file_path, './depot_terrain_save/'+filename)
        except:
            print 'error with ' + file_path
        # if copy success, remove from ftp folder
        else:
            #os.remove(file_path)
