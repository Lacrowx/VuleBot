#!/home/pi/VuleBot/bin/python3

import os
import io
import requests
import hashlib
import discord
from discord.ext import commands
from dotenv import load_dotenv
import sqlite3
from sqlite3 import Error
import random
import asyncio
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.safari.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC


# init discord.py
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
bot = commands.Bot(command_prefix='!')


# init loop
loop = asyncio.get_event_loop()

# init SQLITE
global database
database = r"VuleBot.sqlite3"

def _init_WebDriver():
    # init headless chrome
    webdriver_raspi = "/usr/lib/chromium-browser/chromedriver"
    webdriver_desktop = "/Library/Apple/System/Library/CoreServices/SafariSupport.bundle/Contents/MacOS/safaridriver"
    options = Options()
    options.headless = True

    # Überprüft, auf welchem Gerät VuleBot gestartet wurde und wählt den richtigen Treiber
    if os.path.exists(webdriver_raspi):
        driver = webdriver.Safari()
        print("VuleBot läuft auf einem Raspberry Pi.")
    elif os.path.exists(webdriver_desktop):
        driver = webdriver.Safari()
        print("VuleBot läuft auf einem Desktop-PC.")
    driver.set_window_size(1920, 1080)
    options.add_argument('--lang=de_DE')
    return driver

def create_connection(db_file):
    # create a database connection to the SQLlite database
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_video(conn, video):
    sql = """ INSERT INTO videos (title, posted_date, description, link)
              VALUES(?,?,?,?) 
    """
    cur = conn.cursor()
    cur.execute(sql, video)
    conn.commit()
    return cur.lastrowid

def write_to_db(title, description, link):
    # init db connection
    conn = create_connection(database)

    with conn:
        video = (title, datetime.today().strftime('%d-%m-%Y-%H:%M:%S'), description, link);
        video_id = create_video(conn, video)


def main():
    return


    # # create tables
    # if conn is not None:
    #     create_table(conn, sql_create_videos_table)
    # else:
    #     print("Error, cannot create the database connection.")




@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


@bot.command(name='test', brief="Testet, ob der Bot online ist.")
async def test(ctx):
    if (ctx.channel.id == 813582532120674356 or ctx.channel.id == 452731186360614922):
        response = "VuleBot ist online!"
        print(f'{datetime.now().strftime("%H:%M:%S")}: VuleBot ist online und reagiert auf Nachrichten.')
        await ctx.send(response)
        return
    else:
        print("Command im falschen Channel geposted!")



    await ctx.send(response)


@bot.command(name='video', brief="Das neueste Video mit Valentin abrufen.")
async def video(ctx):
    if (ctx.channel.id == 813582532120674356 or ctx.channel.id == 452731186360614922):
        conn = create_connection(database)
        cur = conn.cursor()
        await ctx.send(f"Gerne schaue ich für dich nach, ob ein neues Video veröffentlicht wurde. Einen Moment.")
        response = get_new_video()

        cur.execute(""" SELECT title, link FROM videos WHERE title=? OR link=?""", (response[1], response[0]))
        result = cur.fetchone()
        if result:
            print("Das Video existiert bereits in der Datenbank")
            print(f'Es gibt kein neues Video. Hier ist Valentins letztes Video mit dem Titel "{response[1]}" {response[0]}')
            await ctx.send(f'''Es gibt kein neues Video. Hier ist Valentins letztes Video.\n\n"{response[1]}" {response[0]}''')

        else:
            print(f'Es gibt ein neues Video mit Valentin! "{response[1]}": {response[0]}')
            await ctx.send(f'Es gibt ein neues Video mit Valentin!\n\n"{response[1]}" {response[0]}')
            write_to_db(response[1], "Ein Video mit Valentin. Placeholder descr.", response[0])
    else:
        print('Command im falschen Channel geposted. VuleBot reagiert nicht.')

@bot.command(name='lastVideo', brief="Ruft das letzte Video aus der Datenbank ab.")
async def lastVideo(ctx):
    response = get_last_video()
    await ctx.send(f'''Hier ist Valentins neuestes bekanntes Video.\n\n"{response[0]}" {response[1]}''')

@bot.command(name='delete', brief="Löscht das letzte Video.")
async def delVideo(ctx):
    await ctx.send(delete_last_video())

async def timer():
    conn = create_connection(database)
    cur = conn.cursor()
    await bot.wait_until_ready()
    #channel = bot.get_channel(515220667470446602) #OR Server
    channel2 = bot.get_channel(813582532120674356) #RL Test-server
    #channel3 = bot.get_channel(452731186360614922) #Powerfun Social Media
    # text_channel_list = []
    # for guild in bot.guilds:
    #     for channel in guild.text_channels:
    #         text_channel_list.append(channel)
    msg_sent = False

    while True:
        if not msg_sent:
            response = get_new_video()
            cur.execute(""" SELECT title, link FROM videos WHERE title=? OR link=?""", (response[1], response[0]))
            result = cur.fetchone()
            if result:
                print(f'{datetime.now().strftime("%H:%M:%S")}: Es scheint kein neues Video mit Vule zu geben.')
                msg_sent = False
                await asyncio.sleep(1800)
            else:
                #await channel.send(f'''Es gibt ein neues Video mit Valentin!\n\nTitel: "{response[1]}"\n{response[0]}''')
                await channel2.send(f'''Es gibt ein neues Video mit Valentin!\n\nTitel: "{response[1]}"\n{response[0]}''')
                #await channel3.send(f'''Es gibt ein neues Video mit Valentin!\n\nTitel: "{response[1]}"\n{response[0]}''')
                write_to_db(response[1], "Ein Video mit Valentin. Placeholder descr.", response[0])
                await asyncio.sleep(1800)
        else:
            msg_sent = False




@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'unhandled message: {args[0]}\n')
            print({args[0]})
        else:
            raise


def get_new_video():

    driver = _init_WebDriver()
    # Beginn der Abfrage
    driver.get("https://rocketbeans.tv/bohnen/155/Valentin")
    driver.get(WebDriverWait(driver, timeout=5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'body > app-root > main > ng-component > section > div > rbtv-media-vod-content-box > section > rbtv-contentbox > div > div > div:nth-child(1) > div > rbtv-media-vod-inline-element:nth-child(1) > figure > figcaption > div > a'))).get_attribute("href"))
    try:
        #driver.find_element_by_css_selector('#rbtv-singlevideo > div > div > div > div.col-12.col-sm-9.col-md-10 > div > button').click()
        WebDriverWait(driver, timeout=5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'body > app-root > main > ng-component > section > rbtv-video-player > div > rbtv-contentlayout > div:nth-child(2) > div > rbtv-video-embed > div > rbtv-embedded-consent > div > div > div > div.col > div > button'))).click()
        print("test")
    except:
        print("Element nicht gefunden.")
    #driver.save_screenshot('screenshot_3.png')
    #driver.switch_to.frame("rbtv-singlevideo")
    WebDriverWait(driver, timeout=5).until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'rbtv-singlevideo')))
    video_link = WebDriverWait(driver, timeout=5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.ytp-title-link'))).get_attribute('href')
    driver.switch_to.default_content()
    video_title = WebDriverWait(driver, timeout=5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'h3.title'))).text
    driver.close()
    return video_link, video_title

def get_last_video():
    # ruft das letzte Video aus der Datenbank ab
    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute("SELECT title, link FROM videos ORDER BY id DESC LIMIT 1")
    result = cur.fetchone()
    return result

def delete_last_video():
    # Löscht das letzte Video in der Datenbank
    conn = create_connection(database)
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM videos WHERE id = (SELECT MAX(id) FROM videos)")
        conn.commit()
        return "Letztes Video erfolgreich gelöscht."
    except Exception as e:
        print(e)
        return "Letztes Video konnte nicht gelöscht werden."

bot.loop.create_task(timer()) #Init loop
bot.run(TOKEN)

if __name__ == '__main__':
    main()

