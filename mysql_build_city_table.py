#!/usr/bin/python

import mysql.connector
import pprint

'''
  Robert Church 2016
   - The purpose of this script is to iterate through the market database and build an indexable city table

'''

def check_if_city_exists(cnx, state_id, city_name):

	cursor = cnx.cursor()
	get_check_if_city_is_in_table = ("SELECT count(city_id) from city_list where `city_name`= %s and `state_id`= %s")

	data = (city_name, state_id)
	cursor.execute(get_check_if_city_is_in_table, data)
	exists = cursor.fetchall()

	return exists[0][0]

def insert_city(cnx, state_id, city_name):

	cursor = cnx.cursor()
	insert_new_city_into_city_list = ("INSERT INTO `city_list` (state_id, country_id, city_name) VALUES (%s, %s, %s)")

	data = (state_id, 0, city_name)
	cursor.execute(insert_new_city_into_city_list, data)
	cnx.commit()


cnx = mysql.connector.connect(user='user', password='password', host='localhost', database='db')
cursor = cnx.cursor()

get_city_list = ("SELECT `city`, `state_id` from marker_details")


cursor.execute(get_city_list)

for row in (cursor.fetchall()):
	city_name = row[0]
	state_id = row[1]
	exists = check_if_city_exists(cnx, state_id, city_name)
	if (exists == 0):
		insert_city(cnx, state_id, city_name)

cnx.close()


