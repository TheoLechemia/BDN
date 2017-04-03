#!/bin/bash

. /home/ubuntu/BDN/settings.ini

TODAY=`date +%F`
DAY=`date +%d`
MONTH=`date +%B |tr 'A-Z' 'a-z'`
YEAR=`date +%y`


#DAILY BACKUP
export PGPASSWORD=Martine50=;pg_dump -h localhost -U onf_admin bdn --format=c --file=/home/ubuntu/sauvegarde_bdd/DAYLY/$TODAY.backup

#MONTHLY BACKUP
if [ $DAY == "01" ]; then
	rm $backup_directory/DAYLY/*
	export PGPASSWORD=Martine50=;pg_dump -h localhost -U onf_admin bdn --format=c --file=/home/ubuntu/sauvegarde_bdd/MONTHLY/$MONTH-$YEAR.backup 
fi





