# -*- coding: utf-8 -*-
import psycopg2
import urllib.parse as urlparse
import os

f = open("players.txt", "r")
temp = f.readlines()

try:
    print(os.getenv("DATABASE_URL"))
    connection = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')

    cursor = connection.cursor()
    
    create_query = """ DROP TABLE IF EXISTS players;
                    CREATE TABLE players (
                    id integer NOT NULL,
                    name text NOT NULL collate "es_VE.utf8",
                    isalive boolean DEFAULT true NOT NULL,
                    deathprob integer DEFAULT 100 NOT NULL,
                    selectprob integer DEFAULT 10 NOT NULL,
                    wins smallint DEFAULT 0 NOT NULL
                    );
                    CREATE SEQUENCE players_id_seq
                    START WITH 1
                    INCREMENT BY 1
                    NO MINVALUE
                    NO MAXVALUE
                    CACHE 1;
                    ALTER SEQUENCE players_id_seq OWNED BY players.id;
                    ALTER TABLE ONLY players ALTER COLUMN id SET DEFAULT nextval('public.players_id_seq'::regclass);
                    ALTER TABLE ONLY players
                    ADD CONSTRAINT players_pkey PRIMARY KEY (id); """

    insert_query = """ INSERT INTO players (name) VALUES (%s)"""

    cursor.execute(create_query)

    for line in temp:
        cursor.execute(insert_query, (line,))
        connection.commit()

except (Exception, psycopg2.Error) as error :
    if(connection):
        print("Error during execution: ", error)
finally:
    #closing database connection.
    if(connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
