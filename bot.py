# bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
client = discord.Client()

@client.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == 'bot test':
        await message.channel.send("testmessage <:pepopeek:574292228198105106>")


client.run(TOKEN)