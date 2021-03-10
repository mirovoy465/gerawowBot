from random import choice as rnd
from discord.ext import commands

class MiscCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)

    @commands.command(name='gerawow',help='gerawow')
    async def gerawow(self,ctx):
        await ctx.send("gerawow")

    @commands.command(name='roll',help='Выдаёт случайное число от 1 до введённого (по умолчанию до 100).')
    async def roll(self,ctx, *, num=100):
        if num<1:
            await ctx.send(rnd(range(num,1)))
        else:
            await ctx.send(rnd(range(1,num+1)))

        
def setup(bot):
    bot.add_cog(MiscCog(bot))