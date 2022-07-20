import discord
from database import Database


class YeetClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))


client = YeetClient()
client.run('NzIzNDg0OTA4MzU3NTUwMTIx.GFKt8M.WoPXl-Ls5pvdkoq9iSUeey2xUODsLc4Ehky1qw')
