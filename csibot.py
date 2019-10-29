# -*- coding: utf-8 -*-
import psycopg2
import random
import tweepy
import time
import sys
import re
from config import BotHelper
from PIL import Image, ImageDraw, ImageFont


class Player:
    def __init__(self, p_id, name, isalive, deathprob, selectprob, wins):
        self.p_id = p_id
        self.name = name
        self.isalive = isalive
        self.deathprob = deathprob
        self.selectprob = selectprob
        self.wins = wins

class CSIBot(BotHelper):
    def __init__(self):
        BotHelper.__init__(self)
        self.api = self.create_api()
        self.player_list = []

    def create_player_list(self, players):
        instance_list = []
        for player in players:
            instance_list.append(Player(player[0], player[1], player[2], player[3], player[4], player[5]))

        return instance_list

    def selectPlayers(self):
        print("Seleccionando jugadores")
        # Get all alive players
        db_player_list = self.query_all("SELECT * FROM players WHERE isalive = true")
        self.player_list = self.create_player_list(db_player_list)
        self.alive_players = len(self.player_list)

        # Check if only one player left
        if (self.alive_players == 1 ):
            # Exit with winner
            self.winner = True
            return self.player_list[0], None;

        # Choose player based on selectprob by id
        killer = random.choices(self.player_list, weights=[player.selectprob for player in self.player_list])
        victim_list = [player for player in self.player_list if player.p_id != killer[0].p_id]

        # Choose victim based on deathprob
        victim = random.choices(victim_list, weights=[victim.deathprob for victim in victim_list])

        # Killer gets more selectprob and less deathprob
        killer[0].deathprob -= 0
        killer[0].selectprob += 0
        killer[0].wins += 1

        # Victim gets killed
        victim[0].isalive = False

        self.alive_players -= 1

        # Return players in a tuple
        print(f"Jugadores seleccionados. {killer[0].name} y {victim[0].name}")
        return killer[0], victim[0];

    def updateDB(self, killer, victim): 
        print("Actualizar BD")
        # Update Killer probabilities
        try:
            update_k_query = """Update players set deathprob = %s, selectprob = %s, wins = %s where id = %s"""
            self.cursor.execute(update_k_query, (killer.deathprob, killer.selectprob, killer.wins, killer.p_id ))
            self.conn.commit()
        except (Exception, psycopg2.Error) as error :
            print ("Error while connecting to PostgreSQL", error)
            self.close()
            sys.exit(1)

        # Update victim status
        try:
            update_v_query = """Update players set isalive = %s where id = %s"""
            self.cursor.execute(update_v_query, (False, victim.p_id ))
            self.conn.commit()
        except (Exception, psycopg2.Error) as error :
            print ("Error while connecting to PostgreSQL", error)
            self.close()
            sys.exit(1)
        
        print("DB actualizada")

    def generatePlayerList(self):
        # Get all players
        print("Generando lista....")
        db_list = self.query_all("SELECT * FROM players ORDER BY name;")
        print("Generada lista de jugadores")
        return self.create_player_list(db_list)

    def draw_image(self, players):
        print("Generando imagen con los nombres")
        max_x = 1760
        max_y = 850
        min_x = 35
        min_y = 35
        img = Image.new('RGB', (max_x, max_y), color = 'white')# 'rgb(200, 200, 200)')
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('/scadrial/twitter-bot/csibot/arial.ttf', size=12, encoding="unic")

        x, y = min_x, min_y
        text_height = draw.textsize('hg')[1] + 15
        text_max_width = 200
        
        for player in players:

            # Set color by status
            if player.isalive:
                color = 'rgb(0, 0, 0)'
                name = player.name
            else:
                color = 'rgb(255, 0, 0)'
                name = self.strike_text(player.name)
                #name = player.name

            if y >= (max_y - min_y):
                x = x + text_max_width
                y = min_y

            draw.text((x, y), name, fill=color, font=font)
            y = y + text_height

        img.save('/scadrial/twitter-bot/csibot/status.png')
        print("Imagen generada")
        return img

    def tweetResults(self, killer, victim):
        # Create a tweet
        print("Creando tweet final")

        # Upload image with player names and status
        status_img = open('/scadrial/twitter-bot/csibot/status.png', 'rb')
        img_id = self.api.media_upload(filename="/scadrial/twitter-bot/csibot/status.png")

        # Calcular semana del evento
        current_date = self.query_all("SELECT * from gamedate;")

        year = current_date[0][0]
        term = current_date[0][1]
        id_db = current_date[0][2]

        name1 = killer.name.strip()

        if victim is not None:
            name2 = victim.name.strip()
            with open('/scadrial/twitter-bot/csibot/temp.txt', 'w') as f:
                f.write(f'{term.capitalize()} Lapso del año {year}.\n\n{name1} HA MATADO a {name2}.\n\nQuedan {self.alive_players} ignacianos.')
        else:
            with open('/scadrial/twitter-bot/csibot/temp.txt', 'w') as f:
                f.write(f'{term.capitalize()} Lapso del año {year}.\n\nEL ÚLTIMO IGNACIANO ES: {name1}.\n\n¡EN TODO AMAR Y SERVIR!')

        if term == "TERCER":
            new_term = "PRIMER"
        elif term == "PRIMER":
            new_term = "SEGUNDO"
            year = year + 1
        elif term == "SEGUNDO":
            new_term = "TERCER"

        print(f"Twitteando resultados {term} {year} jug1: {name1} ")
        try:
            update_t_query = """Update gamedate set year = %s, term = %s where id = %s"""
            self.cursor.execute(update_t_query, (year, new_term.upper(), id_db))
            self.conn.commit()
        except (Exception, psycopg2.Error) as error :
            print ("Error while connecting to PostgreSQL", error)
            self.close()
            sys.exit(1)

        with open('/scadrial/twitter-bot/csibot/temp.txt','r') as f:
            self.api.update_status(f.read(), media_ids=[img_id.media_id_string])

        print("Tweet enviadooo!")
        print("-----------------------------------------------")

def test_run():
    bot = CSIBot()

    while not bot.winner:

        player1, player2 = bot.selectPlayers() # Select players from db and get attributes
        
        if player2 is None:
            break

        bot.updateDB(player1, player2)
        print(f'En esta ronda {player1.name.strip()} HA MATADO A {player2.name.strip()}')
        print(f'Quedan: {bot.alive_players}')
        bot.updateDB(player1, player2)
        print("------------------------------------------------------------------------")
        all_players_list = bot.generatePlayerList()
        bot.draw_image(all_players_list)
        time.sleep(3)

    print(f'Final del juego: {bot.winner}')
    winner = player1
    print(f'HA GANADO: {winner.name}')

    
    bot.close()

def main():
    bot = CSIBot() # Create Bot
    player1, player2 = bot.selectPlayers() # Select killer and victim
    #bot.updateDB(player1, player2) # Update values in DB
    all_players_list = bot.generatePlayerList() # Create list with alive players
    bot.draw_image(all_players_list) # Create image with player names
    bot.tweetResults(player1, player2) # Tweet result with image
    bot.close() # Close db connections
    sys.exit(0)

if __name__ == "__main__":
    main()
    #test_run()