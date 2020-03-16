# -*- coding: utf-8 -*-
import psycopg2
import random
import tweepy
import time
import sys
import re
from config import BotHelper
from PIL import Image, ImageDraw, ImageFont
import logging
from datetime import date
import os

class Player:
    def __init__(self, p_id, name, isalive, deathprob, selectprob, wins):
        self.p_id = p_id
        self.name = name
        self.isalive = isalive
        self.deathprob = deathprob
        self.selectprob = selectprob
        self.wins = wins

class Bot(BotHelper):
    def __init__(self):
        BotHelper.__init__(self)
        self.api = self.create_api()
        self.player_list = []

    def create_player_list(self, players):
        instance_list = []
        for player in players:
            instance_list.append(Player(player[0], player[1], player[2], player[3], player[4], player[5]))

        return instance_list

    def selectPlayer(self):
        print("Seleccionando jugador")
        # Get all alive players
        db_player_list = self.query_all("SELECT * FROM players WHERE isalive = true")
        self.player_list = self.create_player_list(db_player_list)
        self.alive_players = len(self.player_list)

        # Check if only one player left
        if (self.alive_players == 1 ):
            # Exit with winner
            self.winner = True
            return self.player_list[0]

        # Choose player based on selectprob by id
        infected = random.choices(self.player_list, weights=[player.selectprob for player in self.player_list])

        # Killer gets more selectprob and less deathprob
        infected[0].deathprob -= 0
        infected[0].selectprob += 0
        infected[0].wins += 0

        # Victim gets killed
        infected[0].isalive = False

        self.alive_players -= 1

        # Return players in a tuple
        print(f"Jugador infectado. {infected[0].name}")
        return infected[0]

    def updateDB(self, infected): 
        print("Actualizar BD")

        # Update victim status
        try:
            update_v_query = """Update players set isalive = %s where id = %s"""
            self.cursor.execute(update_v_query, (False, infected.p_id))
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
        font = ImageFont.truetype('arial.ttf', size=12, encoding="unic")

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

        img.save('status.png')
        print("Imagen generada")
        return img

    def tweetResults(self, infected):
        # Create a tweet
        print("Creando tweet final")

        # Upload image with player names and status
        status_img = open('status.png', 'rb')
        img_id = self.api.media_upload(filename="status.png")

        # Calcular fecha del evento y otros datos
        #real_infected = self.query_all("SELECT * from data WHERE data_name = 'real_infected';")

        current_date = date.today()
        init_date = date(2020, 3, 15)
        qtn_counter = current_date - init_date

        infected_name = infected.name.strip()

        if not self.winner:
            with open('Temp.txt', 'w') as f:
                f.write(f'Día #{qtn_counter.days} de la cuarentena.\n\n{infected_name} HA DADO POSITIVO POR CORONAVIRUS.\n\nQuedan {self.alive_players} personas sanas.\n\nRecuerden lavarse bien las manos. #COVIDー19')
        else:
            with open('Temp.txt', 'w') as f:
                f.write(f'Día #{qtn_counter.days} de la cuarentena.\n\n¡{infected_name} ES LA ÚLTIMA PERSONA SANA DEL PAÍS, HA CONSEGUIDO LA CURA DEL VIRUS! #COVIDー19')

        print(f"Twitteando resultados {infected_name} ")

        with open('Temp.txt','r') as f:
            self.api.update_status(f.read(), media_ids=[img_id.media_id_string])

        print("Tweet enviadooo!")
        print("-----------------------------------------------")

    def info(self):
        mensajes = [
            'El pánico se propaga más rápido que el virus, recuerda siempre mantener la calma. #COVIDー19',
            'Lávate las manos durante 20 segundos con jabón o desinfectante para elimnar cualquier rastro del virus. #COVIDー19',
            'Evita tocarte los ojos, la nariz y la boca, ya que puedes transferir el virus a tu cuerpo. #COVIDー19',
            'Al toser o estornudar, cúbrete la boca y la nariz con el codo flexionado. #COVIDー19',
            'Evita salir de tu casa al menos que sea totalmente necesario, el distanciamiento social reduce la propagación. #COVIDー19',
            'Mantente informado y sigue las recomendaciones de los profesionales sanitarios y tus autoridades locales. #COVIDー19',
            'Permanezca en casa si empieza a encontrarse mal, aunque se trate de síntomas leves como cefalea y rinorrea leve, hasta que se recupere. #COVIDー19']
        msg = random.choice(mensajes)

        print(msg)
        print('Twitteando mensaje')

        with open('Temp.txt', 'w') as f:
            f.write(msg)

        with open('Temp.txt','r') as f:
            self.api.update_status(f.read())

        print('Tweet enviado')

def test_run():
    bot = Bot()

    while not bot.winner:

        infected = bot.selectPlayer() # Select players from db and get attributes
        
        if bot.winner:
            break

        bot.updateDB(infected)
        print(f'En esta ronda {infected.name.strip()} HA SIDO INFECTADO')
        print(f'Quedan: {bot.alive_players}')
        bot.updateDB(infected)
        print("------------------------------------------------------------------------")
        all_players_list = bot.generatePlayerList()
        bot.draw_image(all_players_list)
        time.sleep(3)

    print(f'Final del juego: {bot.winner}')
    winner = infected
    print(f'HA GANADO: {winner.name}')

    bot.close()

def main():
    bot = Bot() # Create Bot
    #INFECTED = bot.selectPlayer() # Select killer and victim
    #bot.updateDB(INFECTED) # Update values in DB
    all_players_list = bot.generatePlayerList() # Create list with alive players
    bot.draw_image(all_players_list) # Create image with player names
    #bot.tweetResults(INFECTED) # Tweet result with image
    bot.close() # Close db connections
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error falta argumento de ejecucion")
        sys.exit(1)
    else:
        if sys.argv[1] == 'dev':
            test_run()
        elif sys.argv[1] == 'prod':
            main()
        elif sys.argv[1] == 'db':
            BotHelper.create_db()
        elif sys.argv[1] == 'info':
            bot = Bot()
            bot.info()

