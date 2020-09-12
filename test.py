import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
import random
import time
import json
import sqlite3

db_connection = None
db_cursor = None


def connect_db():
    global db_connection
    global db_cursor

    # create database if not existant
    db_connection = sqlite3.connect("mr_yeet.db")
    db_cursor = db_connection.cursor()

    # Create table if not existant
    db_cursor.execute("""CREATE TABLE IF NOT EXISTS "yeet" (
        "discord_user_id" INTEGER NOT NULL PRIMARY KEY UNIQUE,
        "has_yeet" INTEGER NOT NULL,
        "been_yeet" INTEGER NOT NULL);""")

def db_get_data(discord_user_id):
    db_cursor.execute("SELECT * FROM yeet WHERE discord_user_id = {}".format(str(discord_user_id)))
    column = db_cursor.fetchone()

def db_inc_been_yeet(discord_user_id):
    global db_connection
    global db_cursor

    db_cursor.execute("SELECT been_yeet FROM yeet WHERE discord_user_id = {}".format(str(discord_user_id)))
    column = db_cursor.fetchone()

    # Insert a row of data
    if column == None:
        db_cursor.execute("INSERT INTO yeet VALUES(?, 0, ?)", (str(discord_user_id), str(1)))
    else:
        tmp = column[0] + 1
        db_cursor.execute("UPDATE yeet SET been_yeet = ? WHERE discord_user_id = ?", (str(tmp), str(discord_user_id)))

    # Save (commit) the changes
    db_connection.commit()

def db_inc_has_yeet(discord_user_id):
    global db_connection
    global db_cursor

    db_cursor.execute("SELECT has_yeet FROM yeet WHERE discord_user_id = {}".format(str(discord_user_id)))
    column = db_cursor.fetchone()

    # Insert a row of data
    if column == None:
        db_cursor.execute("INSERT INTO yeet VALUES(?, ?, 0)", (str(discord_user_id), str(1)))
    else:
        tmp = column[0] + 1
        db_cursor.execute("UPDATE yeet SET has_yeet = ? WHERE discord_user_id = ?", (str(tmp), str(discord_user_id)))

    # Save (commit) the changes
    db_connection.commit()


connect_db()
# db_inc_has_yeet(24)
db_inc_been_yeet(24)