# -*- coding: utf-8 -*-
import tweepy
import logging
import os
import sys
import psycopg2
import urllib.parse as urlparse

logger = logging.getLogger()

class BotHelper:
    def __init__(self):
        # self.conn = psycopg2.connect(user = "USER",
        #                             password = "PASSWORD",
        #                             host = "HOST",
        #                             port = "PORT",
        #                             database = "DB")
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')
        self.cursor = self.conn.cursor()
        self.consumer_key = os.getenv("CONSUMER_KEY")
        self.consumer_secret = os.getenv("CONSUMER_SECRET")
        self.access_token = os.getenv("ACCESS_TOKEN")
        self.access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
        self.winner = False
        self.alive_players = 0
    
    def version(self):
        self.cursor.execute("SELECT version();")
        record = self.cursor.fetchone()
        print("You are connected to - ", record,"\n")

    def close(self):
        if(self.conn):
            self.cursor.close()
            self.conn.close()

    def query_all(self, query):
        try:
            self.cursor.execute(query)
            db_result = self.cursor.fetchall()
            return db_result
                        
        except (Exception, psycopg2.Error) as error :
            print ("Error while connecting to PostgreSQL", error)
            self.close()
            sys.exit(1)

    def create_api(self):
        # Auth to twittter api
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)

        # Create api object
        api = tweepy.API(auth, wait_on_rate_limit=True, 
            wait_on_rate_limit_notify=True)

        # Verify keys are correct
        try:
            api.verify_credentials()
        except Exception as e:
            logger.error("Error creating API", exc_info=True)
            raise e

        logger.info("API created")
        return api

    def strike_text(self, text):
        result = ''
        for c in text:
            result = result + '\u0336' + c
        return result

    @staticmethod
    def create_db():
        f = open("players.txt", "r")
        temp = f.readlines()

        try:
            print("conectando a db")
            connection = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')

            cursor = connection.cursor()

            print('crear tabla players')
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
            print('carga datos')
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

if __name__ == "__main__":
    pass
