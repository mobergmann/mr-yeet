import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
import random
import time
import json

#region config and token
config_file = open("config.json", "r").read()
config = json.loads(config_file)
token = config["token"]
print(token)
#endregion