import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
import random
import time
import json

import json

#region config and token

config_file = open("config.json", "r").read()
config = json.loads(config_file)
token = config["token"]

#endregion

#region function

async def _yeet(ctx, should_kick):
    yeet_voice_channel = ctx.author.voice.channel

    # get users which can be yeetet
    users_to_yeet = ctx.author.voice.channel.members

    # get user to yeet
    user_to_yeet = users_to_yeet[random.randint(0,len(users_to_yeet)-1)]
    yeet_channel = discord.utils.find(lambda x: x.name == 'YEET-LAUNCH', ctx.guild.channels)

    # connect bot to voice
    voice = await yeet_voice_channel.connect() # bot.voice.join_voice_channel(yeet_voice_channel)
    
    # play yeet sound
    player = voice.play(discord.FFmpegPCMAudio('YEET.mp3'))
    time.sleep(1)

    # yeet user form voice channel
    for user in users_to_yeet:
        if user_to_yeet == user:
            if should_kick:
                await user_to_yeet.move_to(None)
            else:
                await user_to_yeet.move_to(yeet_channel)

    # inform, that bot has yeetet user x
    await ctx.channel.send("Yeetet {}".format(ctx.author))
    
    # disconnect bot from voice channnel
    await voice.disconnect()

#endregion

#region bot & command

bot = commands.Bot(command_prefix='/')

@bot.command()
async def yeet(ctx):
    if ctx.author.bot:
        return
    if ctx.author.voice.channel == None:
        return

    await _yeet(ctx, False)

@bot.command()
async def yeetkick(ctx):
    if ctx.author.bot:
        return
    if ctx.author.voice.channel == None:
        return

    await _yeet(ctx, True)

@bot.command()
async def yeetrestart(ctx):
    pass

# endregion

bot.run(token)