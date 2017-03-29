#!/bin/bash

. /home/ubuntu/BDN/settings.ini

TODAY=`date +%F`
DAY=`date +%d`
MONTH=`date +%B |tr 'A-Z' 'a-z'`
YEAR=`date +%y`


#DAILY BACKUP
export PGPASSWORD=$user_bdn_pass;pg_dump -h localhost -U $user_bdn --format=c --file=$backup_directory/DAYLY/$TODAY.backup bdn

#MONTHLY BACKUP
if [ $DAY == "01" ]; then
	rm $backup_directory/DAYLY/*
	export PGPASSWORD=$user_bdn_pass;pg_dump -h localhost $user_bdn --format=c --file=$backup_directory/MONTHLY/$MONTH-$YEAR.backup bdn
fi