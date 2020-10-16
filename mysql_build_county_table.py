#!/usr/bin/python

import mysql.connector
import pprint

'''
  Robert Church 2016
   - The purpose of this script is to iterate through the market database and build an indexable county table

'''


def check_if_county_exists(cnx, state_id, county_name):

	cursor = cnx.cursor()
	get_check_if_county_is_in_table = ("SELECT count(county_id) from county_list where `county_name`= %s and `state_id`= %s")

	data = (county_name, state_id)
	cursor.execute(get_check_if_county_is_in_table, data)
	exists = cursor.fetchall()

	return exists[0][0]

def insert_county(cnx, state_id, county_name):

	cursor = cnx.cursor()
	insert_new_county_into_county_list = ("INSERT INTO `county_list` (state_id, country_id, county_name) VALUES (%s, %s, %s)")

	data = (state_id, 0, county_name)
	cursor.execute(insert_new_county_into_county_list, data)
	cnx.commit()


cnx = mysql.connector.connect(user='user', password='pass', host='localhost', database='db')
cursor = cnx.cursor()

get_county_list = ("SELECT `county`, `state_id` from marker_details")


cursor.execute(get_county_list)

for row in (cursor.fetchall()):
	county_name = row[0]
	state_id = row[1]
	exists = check_if_county_exists(cnx, state_id, county_name)
	if (exists == 0):
		insert_county(cnx, state_id, county_name)

cnx.close()


