#!/usr/bin/python

import csv
import mysql.connector
import pprint
import utm

'''
  Robert Church 2016
   - The purpose of this script is to iterate through the GIS marker table and convert UTM to LAT/LONG.

'''


cnx = mysql.connector.connect(user='user', password='pass', host='localhost', database='db')
cursor = cnx.cursor()

get_markers = ("SELECT `marker_details_id`,`utm_zone`,`utm_north`,`utm_east` from marker_details where utm_zone != 0 and utm_north != 0 and utm_east !=0")
update_lat_lon_marker = ("UPDATE marker_details set marker_lat=%s, marker_lon=%s where marker_details_id = %s limit 1")


cursor.execute(get_markers)

for row in (cursor.fetchall()):
	id = row[0]
	utm_zone = row[1]
	utm_north = row[2]
	utm_east = row[3]
	print id, utm_north, utm_east
	lat_lon = utm.to_latlon(utm_east, utm_north, utm_zone, northern=True)
	lat = lat_lon[0]
	lon = lat_lon[1]
	data = (lat, lon, id)
	cursor.execute(update_lat_lon_marker, data)
	cnx.commit()
	pprint.pprint(cursor._executed)

cnx.close()

