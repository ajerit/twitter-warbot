# -*- coding: utf-8 -*-
import tweepy
import logging
import os
import sys
import psycopg2

logger = logging.getLogger()

class BotHelper:
    def __init__(self):
        self.conn = psycopg2.connect(user = "USER",
                                    password = "PASSWORD",
                                    host = "HOST",
                                    port = "PORT",
                                    database = "DB")
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

if __name__ == "__main__":
    pass
