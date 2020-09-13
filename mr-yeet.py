#region import
import asyncio
import datetime
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
import random
import time
import json
import os
import sys
import pathlib
import sqlite3
#endregion


#region globals (config, token and database)

# Config
config_file = open("config.json", "r").read()
config = json.loads(config_file)
token = config["token"]

bot = commands.Bot(command_prefix="/")

# Database
db_connection = None
db_cursor = None

# Ranks
yeet_ranks = [
    ("Unfortunatet Yeeter", 0),
    ("Yeet Beginner", 1),
    ("Yeet Trainee", 3),
    ("Yeet Approved", 5),
    ("Yeet Adept", 7),
    ("Big Yeeter", 9),
    ("Boss Yeeter", 10),
    ("Grand Yeeter", 11),
    ("Yeet King", 12),
    ("Yeet Emperor", 13),
    ("Grand Yeet Emperor", 14)
]


#endregion


#region functions

#region Database
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
    return db_cursor.fetchone()

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
#endregion

#region yeet specific
def get_yeet_rank(yeet_score):
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

def get_yeet_sound():
    # get all files (yeet sounds) in the sounds folder
    yeet_sounds = []
    for (dirpath, dirnames, filenames) in os.walk("sounds/"):
        yeet_sounds.extend(filenames)
        break

    # select an random yeet sound
    return "sounds" + os.path.sep + random.choice(yeet_sounds)

async def _yeet(ctx, should_kick):
    #region Error Check
    yeet_voice = ctx.author.voice

    # if user is not in a voice channel, then inform the user
    if yeet_voice == None:
        log("{} is not connected to a voice channel".format(ctx.author))
        await send_dm(ctx.author, "Please only summmon me when you are connected to a chanel on a guild")
        return

    yeet_voice_channel = yeet_voice.channel

    # if user is not connected to a voice channel
    if yeet_voice_channel == None:
        log("{} is not connected to a voice channel".format(ctx.author))
        await send_dm(ctx.author, "Please only summmon me when you are connected to a chanel on a guild")
        return

    # if message guild is different from user voice channel inform the user
    if ctx.guild != yeet_voice_channel.guild:
        log("{} used yeet on a guild to which he wasn't connected".format(ctx.author))
        await send_dm(ctx.author, "Please only summmon me on a guild, when you are also connected to a voicechanel on that guild.")
        return


    # get yeet channel from server
    # can either be a channel called YEET-LAUNCH, or if the channel doesn't exist the afk channel
    yeet_channel = discord.utils.find(lambda x: x.name == "YEET-LAUNCH", ctx.guild.channels)
    if yeet_channel == None:
        yeet_channel = ctx.guild.afk_channel
        if yeet_channel == None:
            try:
                await ctx.channel.send("I cannot use my yeet powers, because I need a channel with the name YEET-LAUNCH, or a AFK channel. Please create one.")
                return
            except e:
                log(str(e))
                return

    # if user already connected to yeet channel
    if yeet_voice_channel == yeet_channel:
        log("{} used yeet in the yeet channel".format(ctx.author))
        await send_dm(ctx.author, "Please don't summmon me when you are alreay connected to the yeet_cannel.")
        return
    #endregion

    # get users which can be yeetet
    users_to_yeet = ctx.author.voice.channel.members

    # get user to yeet
    user_to_yeet = random.choice(users_to_yeet)

    # connect bot to voice
    voice = None
    try:
        voice = await yeet_voice_channel.connect()
    except e:
        log(str(e))
        return

    # play yeet sound
    player = voice.play(discord.FFmpegPCMAudio(get_yeet_sound()))
    time.sleep(1) # wait for the sound to be finished playing

    # yeet user form voice channel
    for user in users_to_yeet:
        if user_to_yeet == user:
            if should_kick:
                try:
                    await user_to_yeet.move_to(None) # disconnect from voice
                except e:
                    log(str(e))
                    return
                break
            else:
                try:
                    await user_to_yeet.move_to(yeet_channel) # move into yeet channel
                except e:
                    log(str(e))
                    return
                break

    # log yeet action
    if should_kick:
        log("{} yeetkicked {}".format(ctx.author, user_to_yeet))
    else:
        log("{} yeeted {}".format(ctx.author, user_to_yeet))

    # inform, that bot has yeetet a user
    await ctx.channel.send("Yeeted {}".format(user_to_yeet))

    #region add informatoin to database
    try:
        db_inc_has_yeet(ctx.author.id)
    except e:
        log("Could not save yeet of {} to database, bechause of: ".format(ctx.author.id) + str(e))

    try:
        db_inc_been_yeet(user_to_yeet.id)
    except e:
        log("Could not save yeet of {} to database, bechause of: ".format(user_to_yeet.id) + str(e))
    #endregion

    # disconnect bot from voice channnel
    await voice.disconnect()
#endregion


def log(message):
    print("{}: {}".format(datetime.datetime.now(), message))

async def send_dm(user, message):
    try:
        dm_channel = user.dm_channel
        if dm_channel == None:
            dm_channel = await user.create_dm()
        await dm_channel.send(message)
    except e:
        log("could not send dm to {}. See: {}".format(user, str(e)))
        return False
#endregion


#region bot & command

@bot.command()
async def yeet(ctx):
    if ctx.author.bot:
        return

    await _yeet(ctx, False)

@bot.command()
async def yeetkick(ctx):
    if ctx.author.bot:
        return

    await _yeet(ctx, True)

@bot.command()
async def yeetscore(ctx):
    yeet_score = 0
    has_yeet = 0
    been_yeet = 0

    # get data from database an handle errors or no database entry
    data = None
    try:
        data = db_get_data(ctx.author.id)
    except e:
        log("Could no retrive database information of {}, because of {}".format(ctx.author, str(e)))
    if data == None:
        data = [ctx.author.id, 0, 0]

    # fill data into variables
    has_yeet = data[1]
    been_yeet = data[2]

    # when been_yeet == 0, then yeet_score := has_yeet / 1
    # otherwise yeet_score := has_yeet / (been_yeet * 0.3)
    if been_yeet == 0:
        yeet_score = has_yeet
    else:
        yeet_score = has_yeet / been_yeet


    # get the yeet rank of the user
    yeet_rank = get_yeet_rank(yeet_score=yeet_score)

    # creating the yeat_score embed
    embed = discord.Embed(title = "Yeet Score: {}".format(round(yeet_score, 2)), color = 0xd97355)
    embed.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
    embed.add_field(name = "Times Yeetet Somone", value = str(has_yeet), inline = False)
    embed.add_field(name = "Times Has been Yeetet", value = str(been_yeet), inline = False)
    embed.set_footer(text = "Your Yeet Rank is: \"{}\"".format(yeet_rank))

    # semding the score and logging
    try:
        await ctx.channel.send(embed=embed)
    except e:
        log("Could no send score of {}, because of {}".format(ctx.author, str(e)))

    log("{} retrieved its Yeets Score".format(ctx.author))

@bot.event
async def on_ready():
    log("Bot is running...")
    connect_db()
# endregion

log("Bot is starting...")
bot.run(token)