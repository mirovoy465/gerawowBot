from random import choice as rnd
from time import sleep
from typing import Optional
from discord.ext import commands
from discord.ext.commands import Greedy
from discord import Member

class MiscCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)


    @commands.command(name='roll',help='Выдаёт случайное число от 1 до введённого (по умолчанию до 100).')
    async def roll(self, ctx, num:int=100):
        if num<1:
            await ctx.send(rnd(range(num,1)))
        else:
            await ctx.send(rnd(range(1,num+1)))


    @commands.command(name="mute")
    async def mute(self, ctx, targets:Greedy[Member], hours:Optional[int]):
        for target in targets:
            await target.edit(mute=True)
            print(f'muted {target.name} for {hours} hours' )
            if hours:
                await sleep(hours)
                await target.edit(mute=False)
                print(f'{target.name} unmuted!' )
        

        await ctx.channel.purge(limit=2)
    
    @commands.command(name="unmute")
    async def unmute(self, ctx, targets:Greedy[Member], hours:Optional[int]):
        for target in targets:
            await target.edit(mute=False)
        await ctx.channel.purge(limit=2)

def setup(bot):
    bot.add_cog(MiscCog(bot))