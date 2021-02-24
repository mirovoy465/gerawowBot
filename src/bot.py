# bot.py
import os
import discord
import random
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot("gw!")

@bot.event
async def on_ready():
    print(f'{bot.user} ready!')
    bot.load_extension('cogs.music')

@bot.command(name='gerawow',help='gerawow')
async def gerawow(ctx):
    await ctx.send("testmessage <:pepopeek:574292228198105106>")

@bot.command(name='roll',help='Returns a random number')
async def roll(ctx, num : int):
    await ctx.send(random.choice(range(1,num+1)))


bot.run(TOKEN)