#!/usr/bin/python

import csv
import mysql.connector

'''

  Robert Church 2017
  - The purpose of this script is to import data from CSV file directly into the database.
  - This script iteration takes the Texas marker database, hard sets the state (44) and imports the markers

'''


cnx = mysql.connector.connect(user='user', password='pass', host='localhost', database='db')
cursor = cnx.cursor()

add_marker = ("INSERT INTO marker_details "
             "(marker_id, state_id, markernum, title, indexname, address, city, county, countyId, utm_zone, utm_east, utm_north, code, year, rthl, loc_desc, size, markertext ) "
             "VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )") 


# markernum,title,indexname,address,city,county,countyId,utm_zone,utm_east,utm_north,code,year,rthl,loc_desc,size,markertext,atlas_number
csv.register_dialect('excel', delimiter=',')

with open('test.csv', 'r') as f:
    reader = csv.reader(f, dialect='excel')
    for row in reader:
        data_marker = ('', '44', row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15] )
	cursor.execute(add_marker, data_marker)
	cnx.commit()

    cnx.close()

