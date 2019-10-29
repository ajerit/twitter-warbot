# -*- coding: utf-8 -*-
import psycopg2

f = open("players.txt", "r")
temp = f.readlines()

try:
	connection = psycopg2.connect(user = "USER",
                                password = "PASSWORD",
                                host = "HOST",
                                port = "PORT",
                                database = "DB")

	cursor = connection.cursor()

	insert_query = """ INSERT INTO players (name) VALUES (%s)"""

	for line in temp:
		cursor.execute(insert_query, (line,))
		connection.commit()

except (Exception, psycopg2.Error) as error :
    if(connection):
        print("Failed to insert record into player table", error)
finally:
    #closing database connection.
    if(connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
