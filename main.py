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

#region config and token

config_file = open("config.json", "r").read()
config = json.loads(config_file)
token = config["test_token"]

#endregion

#region function

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
    
async def _yeet(ctx, should_kick):
    #region Error Check

    yeet_voice = ctx.author.voice

    # if user is not in a voice channel, then inform the user
    if yeet_voice == None:
        log("{} is not connected to a voice channel".format(ctx.author))
        await send_dm(ctx.author, "Please only summmon me when you are connected to a chanel on a guild")
        return
        
    yeet_voice_channel = yeet_voice.channel
    
    # if message guild is different from user voice channel inform the user
    if yeet_voice_channel == None:
        log("{} is not connected to a voice channel".format(ctx.author))
        await send_dm(ctx.author, "Please only summmon me when you are connected to a chanel on a guild")
        return

    if ctx.guild != yeet_voice_channel.guild:
        log("{} used yeet on a guild to which he wasn't connected".format(ctx.author))
        await send_dm(ctx.author, "Please only summmon me on a guild, when you are also connected to a voicechanel on that guild.")
        return

    #endregion

    # get users which can be yeetet
    users_to_yeet = ctx.author.voice.channel.members

    # get user to yeet
    user_to_yeet = users_to_yeet[random.randint(0,len(users_to_yeet)-1)]

    # get yeet channel from server
    # can either be a channel called YEET-LAUNCH, or if the channel doesn't exist a afk channel
    yeet_channel = discord.utils.find(lambda x: x.name == 'YEET-LAUNCH', ctx.guild.channels)
    if yeet_channel == None:
        yeet_channel = ctx.guild.afk_channel
        if yeet_channel == None:
            try:
                await ctx.channel.send("I cannot use my yeet powers, because I need a channel with the name YEET-LAUNCH, or a AFK channel. Please create one.")
                return
            except e:
                log(e)

    # connect bot to voice
    voice = None
    try:
        voice = await yeet_voice_channel.connect()                
    except e:
        log(e)
        return

    # play yeet sound
    player = voice.play(discord.FFmpegPCMAudio("YEET.mp3"))
    time.sleep(1) # wait for the sound to be finished

    # yeet user form voice channel
    for user in users_to_yeet:
        if user_to_yeet == user:
            if should_kick:
                try:
                    await user_to_yeet.move_to(None)
                except e:
                    log(e)
                    return
                break
            else:
                try:
                    await user_to_yeet.move_to(yeet_channel)
                except e:
                    log(e)
                    return
                break

    # inform, that bot has yeetet user x
    await ctx.channel.send("Yeetet {}".format(ctx.author))
    
    # disconnect bot from voice channnel
    await voice.disconnect()

#endregion

#region bot & command

bot = commands.Bot(command_prefix='/')

@bot.command()
async def yeet(ctx):
    log("{} called yeet".format(ctx.author))

    if ctx.author.bot:
        return

    await _yeet(ctx, False)

@bot.command()
async def yeetkick(ctx):
    log("{} called yeetkick".format(ctx.author))

    if ctx.author.bot:
        return

    await _yeet(ctx, True)

# endregion

log("Starting Mr Yeet")
bot.run(token)