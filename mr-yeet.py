#region import

import asyncio
import datetime
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
import math
import random
import time
import json
import os
import sys
import pathlib
import sqlite3

#endregion

class DB_User:
    id = None
    has_yeet = None
    been_yeet = None
    yeet_coins = None
    yeet_shield_last_activated = None
    
    is_default_user = True # if the user object is not present in the database
    
    def __init__(self, id, has_yeet, been_yeet, yeet_coins, yeet_shield_last_activated, is_default_user=False):
        self.id = id
        self.has_yeet = has_yeet
        self.been_yeet = been_yeet
        self.yeet_coins = yeet_coins
        self.yeet_shield_last_activated = None if yeet_shield_last_activated == None or yeet_shield_last_activated == 'None' else datetime.datetime.strptime(yeet_shield_last_activated, "%Y-%m-%d %H:%M:%S.%f")
        self.is_default_user = is_default_user
    
    @staticmethod
    def default_user(id:int):
        return DB_User(id=id, has_yeet=0, been_yeet=0, yeet_coins=0, yeet_shield_last_activated=None, is_default_user=True)

#region globals (config, token and database)

# Config
SOFT_TIME = 2

config_file = open("config.json", "r").read()
config = json.loads(config_file)
token = config["test_token"]

bot = commands.Bot(command_prefix="/")

# Database
db_connection = None
db_cursor = None

# Ranks
yeet_ranks = [
    ("Unfortunate Yeeter", 0),
    ("Yeet Beginner", 1),
    ("Yeet Trainee", 3),
    ("Yeet Approved", 5),
    ("Yeet Adept", 7),
    ("Big Yeeter", 9),
    ("Yeet Schmied", 11),
    ("Yeetlead", 13),
    ("Boss Yeeter", 15),
    ("Grand Yeeter", 17),
    ("Yeet King", 18),
    ("Yeet Emperor", 19),
    ("Grand Yeet Emperor", 20)
]

#endregion


#region Functions

#region Database

def connect_db():
    """connect to the given database"""
    global db_connection
    global db_cursor

    # create database if not existant
    db_connection = sqlite3.connect("mr_yeet.db")
    db_cursor = db_connection.cursor()

    # Create table if not existant
    db_cursor.execute("""CREATE TABLE IF NOT EXISTS "yeet" (
        "discord_user_id"	INTEGER NOT NULL UNIQUE,
        "has_yeet"	INTEGER NOT NULL,
        "been_yeet"	INTEGER NOT NULL,
        "yeet_coins"	INTEGER NOT NULL DEFAULT 0,
        "yeet_shield_last_activated"	TEXT,
        PRIMARY KEY("discord_user_id")
    );""")

def db_get(id:int) -> DB_User:
    """returns the column of the user with the given user id"""

    db_cursor.execute("SELECT * FROM yeet WHERE discord_user_id = {}".format(str(id)))
    column = db_cursor.fetchone()

    if column == None:
        return DB_User.default_user(id)
    else:
        return DB_User(id=column[0], has_yeet=column[1], been_yeet=column[2], yeet_coins=column[3], yeet_shield_last_activated = column[4])

# TODO better solution for update or isert logic
def db_update(user:DB_User):
    """updates a database column with the given id. if the column doesn't exist, then it creates a new column"""
    global db_connection
    global db_cursor

    if user.is_default_user:
        db_cursor.execute(
            "INSERT INTO yeet VALUES(?, ?, ?, ?, ?)",
            (str(user.id), str(user.has_yeet), str(user.been_yeet), str(user.yeet_coins), str(user.yeet_shield_last_activated)))
    else:
        db_cursor.execute(
            "UPDATE yeet SET has_yeet = ?, been_yeet = ?, yeet_coins = ?, yeet_shield_last_activated = ? WHERE discord_user_id = ?", 
            (str(user.has_yeet), str(user.been_yeet), str(user.yeet_coins), str(user.yeet_shield_last_activated), str(user.id)))

    # Save (commit) the changes
    db_connection.commit()

#endregion

#region yeet

# TODO return the remaining time
def yeet_shield_remaining_time(user:DB_User):
    """returns the remaining time the yeet shield is active"""
    
    if user.yeet_shield_last_activated == None:
        return "0"
    else:
        expiration_date = user.yeet_shield_last_activated + datetime.timedelta(days=1)

        if str(expiration_date) < str(datetime.datetime.now()):
            return "0"
        else:
            time_delta = expiration_date - datetime.datetime.now()

            s = time_delta.seconds
            hours = s // 3600
            s = s - (hours * 3600)
            minutes = s // 60
            seconds = s - (minutes * 60)
            time_string = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

            return time_string

def get_yeet_user(users:list):
    """returns a list od users which doesn't have yeet shield activated"""
    ret_users = []
    for i_user in users:
        user = db_get(i_user.id)

        if user.is_default_user: # user not in db
            ret_users.append(i_user)
            continue
        elif user.yeet_shield_last_activated == None: # no shield
            ret_users.append(i_user)
            continue

        expiration_date = datetime.strptime(user.yeet_shield_last_activated) + datetime.timedelta(days=1)
        if yeet_shield_remaining_time(user=user): # shield expired
            ret_users.append(i_user)
            continue
        
    if len(ret_users) == 0:
        return None
    else:
        return ret_users

def get_yeet_rank(yeet_score:int):
    """returns the yeet score spesific yeet rank"""
    # make secrets
    if 0 < yeet_score <= 0.01:
        return "Shitty Yeeter"
    if yeet_score >= 35:
        return "The Yeeter of all Yeeters"

    # calculate the yeat rank of the user
    for i in range(len(yeet_ranks)-1):
        if yeet_ranks[i][1] <= yeet_score < yeet_ranks[i+1][1]:
            return yeet_ranks[i][0]
    return yeet_ranks[len(yeet_ranks)-1][0] # prevent an out of bounds


async def _yeet(ctx, should_kick:bool=False, move_back:bool=False):
    """the main yeet logic"""
    #region Error Check

    # get user from database
    db_yeeter = db_get(id=ctx.author.id)
    if db_yeeter.is_default_user: # user not found in Database, assign default attributes
        db_yeeter = DB_User.default_user()

    # if yeet_caller has shield activated cancel yeet
    if yeet_shield_remaining_time(db_yeeter) > 0:
        send_dm(ctx.author, "You can't yeet when you are protected by the power of the magic (and expensive) yeet shield.")


    # if user is not connected to a voice channel
    if ctx.author.voice == None or ctx.author.voice.channel == None:
        await send_dm(ctx.author, "Please only summmon me when you are connected to a channel on a guild.")
        return

    yeet_voice = ctx.author.voice
    yeet_voice_channel = yeet_voice.channel # the origin channel in which mr yeet has been summond
    
    # if message guild is different from user voice channel inform the user
    if ctx.guild != yeet_voice_channel.guild:
        await send_dm(ctx.author, "Please only summmon me on a guild, to which you are connected.")
        return

    # get yeet channel from server
    # can either be a channel called YEET-LAUNCH, or if the channel doesn't exist the afk channel
    yeet_channel = discord.utils.find(lambda x: x.name == "YEET-LAUNCH", ctx.guild.channels)
    if yeet_channel == None:
        yeet_channel = ctx.guild.afk_channel
        if yeet_channel == None:
            await ctx.channel.send("I cannot use my yeet powers, because I need a channel with the name YEET-LAUNCH, or an AFK channel. Please create one of these.")
            
    # if user already connected to yeet channel
    if yeet_voice_channel == yeet_channel:
        await send_dm(ctx.author, "Please don't summmon me when you are alreay connected to the yeet_cannel.")
        return
    
    #endregion

    # get users which can be yeetet
    users_to_yeet = get_yeet_user(yeet_voice_channel.members)

    if users_to_yeet == None or len(users_to_yeet) == 0:
        await send_dm(ctx.author, "You are not connceted to a cannel with a user which can be yeetet.")
        return

    # get user to yeet
    user_to_yeet = random.choice(users_to_yeet)

    # connect bot to voice
    voice = None
    try:
        voice = await yeet_voice_channel.connect()
    except Exception as e:
        log(str(e))
        return

    # play yeet sound
    try:
        player = voice.play(discord.FFmpegPCMAudio("sounds"+os.path.sep+"yeet.mp3"))
    except Exception as e:
        log(str(e))
        return
    time.sleep(1) # wait for the sound to be finished playing

    # yeet user form voice channel
    await user_to_yeet.move_to(None if should_kick else yeet_channel) # yeetick or yeet
    
    # disconnect bot from voice channnel
    await voice.disconnect()

    # inform, that bot has yeetet a user
    await ctx.channel.send("Yeeted {}".format(user_to_yeet))

    #region add informatoin to database

    db_yeeter.has_yeet+=1
    # add yeet coin
    db_yeeter.yeet_coins += 0.04 # per yeet add 0.04 yeet coins (after 25 yeets you have 1 yeet coin)
    db_update(db_yeeter) # save changes

    user_to_yeet_data = db_get(user_to_yeet.id)
    user_to_yeet_data.been_yeet+=1
    db_update(user_to_yeet_data)

    #endregion

    # soft yeet
    if move_back:
        time.sleep(SOFT_TIME) # wait for the soft time to finish
        await user_to_yeet.move_to(yeet_voice_channel) # move back to origin channel

#endregion


def log(message):
    print("{}: {}".format(datetime.datetime.now(), message))

async def send_dm(user, message):
    try:
        dm_channel = user.dm_channel
        if dm_channel == None:
            dm_channel = await user.create_dm()
        await dm_channel.send(message)
    except Exception as e:
        log("could not send dm to {}. See: {}".format(user, str(e)))
        return False
#endregion


#region bot & command

@bot.command()
async def yeethelp(ctx):
    embed=discord.Embed(
        title="Yeet Manual",
        url="https://github.com/mobergmann/mr-yeet#usage",
        description="This is a manual to improve your yeet skills.",
        color=0xff65c4)
    embed.add_field(
        name="/yeethelp",
        value="If you need help type `/yeethelp`! Prints a help page (in case you didn't notice, this page).",
        inline=False)
    embed.add_field(
        name="/yeet",
        value="Moves a random user into a channel called **YEET-LAUNCH** or if not exist into the guilds **AFK** channel.",
        inline=False)
    embed.add_field(
        name="/yeetsoft",
        value=" Like `/yeet` but moves the user back into the origin channel after 2 seconds.",
        inline=False)
    embed.add_field(
        name="/yeetkick",
        value=" Like `/yeet` but doesn't move the user into the yeet channel, instead disconnects the user from the server.",
        inline=False)
    embed.add_field(
        name="/yeetshield",
        value="Activates a Yeet Shield. When a Yeet Shield is activated, you cannot be yeetet anymore.",
        inline=False)
    embed.add_field(
        name="/yeetaccount",
        value="Shows the yeet stats of the player. Yeet Score, Yeet Coins and Yeet Shield.",
        inline=False)
    embed.set_footer(
        text="Good luck yeeting!")
    
    await ctx.channel.send(embed=embed)

@bot.command()
async def yeet(ctx):
    if ctx.author.bot:
        return

    await _yeet(ctx)

@bot.command()
async def yeetkick(ctx):
    if ctx.author.bot:
        return

    await _yeet(ctx, should_kick=True)

@bot.command()
async def yeetsoft(ctx):
    if ctx.author.bot:
        return

    await _yeet(ctx, move_back=True)

@bot.command()
async def yeetaccount(ctx):
    # get data from database an handle errors or no database entry
    user = db_get(ctx.author.id)

    # when been_yeet == 0, then yeet_score := has_yeet / 1
    # otherwise yeet_score := has_yeet / (been_yeet / 35)
    if user.been_yeet == 0:
        yeet_score = user.has_yeet
    else:
        yeet_score = (user.has_yeet / user.been_yeet) + (user.has_yeet / 35)

    # get the yeet rank of the user
    yeet_rank = get_yeet_rank(yeet_score=yeet_score)

    # creating the yeat_score embed
    embed = discord.Embed(
        title = "Yeet Account",
        url = "https://github.com/mobergmann/mr-yeet",
        description="Your personal Yeet passport. All the yeet you need!",
        color = 0xd97355)
    embed.set_author(
        name = ctx.author.name,
        icon_url = ctx.author.avatar_url)

    embed.add_field(
        name = "‎",
        value = str("**__Yeet Stats__**"),
        inline = False)

    embed.add_field(
        name = "Yeet Score",
        value = str(round(yeet_score, 2)),
        inline = True)
    embed.add_field(
        name = "Yeet Rank",
        value = yeet_rank,
        inline = True)
    embed.add_field(
        name = "‎",
        value = "‎",
        inline = True)
        
    embed.add_field(
        name = "Times Yeetet",
        value = str(user.has_yeet),
        inline = True)
    embed.add_field(
        name = "Times been Yeetet",
        value = str(user.been_yeet),
        inline = True)
    embed.add_field(
        name = "‎",
        value = "‎",
        inline = True)

    embed.add_field(
        name = "‎",
        value = "**__Yeet Wallet__**",
        inline = False)

    embed.add_field(
        name = "Yeet Coins",
        value = str(round(user.yeet_coins, 2)),
        inline = False)

    yeet_shield_time = yeet_shield_remaining_time(user=user)
    
    embed.add_field(
        name = "Yeet Shield",
        value = "inactive" if yeet_shield_time == "0" else "active",
        inline = True)
    embed.add_field(
        name = "Remaining",
        value =  "0" if yeet_shield_time == "0" else yeet_shield_time,
        inline = True)
    
    
    # semding the score and logging
    await ctx.channel.send(embed=embed)

@bot.command()
async def yeetshield(ctx):
    db_user = db_get(ctx.author.id)
    db_user.yeet_shield_last_activated = str(datetime.datetime.now())
    db_update(db_user)

    # get yeet score
    # subtract 0.5 yeet points
    # if erg is smaller than 0, than print error and undo
    # 

@bot.event
async def on_ready():
    log("Bot is running...")
    connect_db()
# endregion

log("Bot is starting...")
bot.run(token)