from random import choice as rnd
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


    @commands.command(name='clear',help='Удаляет необходимое количество сообщений')
    async def clear(self, ctx, num:int=1):
        if checkRole(self,ctx): await ctx.channel.purge(limit=num+1)
        else: await ctx.channel.send(f'иди нахуй {ctx.author.name}')


    @commands.command(name="mute")
    async def mute(self, ctx, targets:Greedy[Member]):
        await ctx.channel.purge(limit=1)
        if checkRole(self,ctx): 
            for target in targets:
                await target.edit(mute=True)
                print(f'muted {target.name}' )
        else: await ctx.channel.send(f'иди нахуй {ctx.author.display_name}')
    
        
    
    @commands.command(name="unmute")
    async def unmute(self, ctx, targets:Greedy[Member]):
        if checkRole(self,ctx): 
            for target in targets:
                await target.edit(mute=False)
            await ctx.channel.purge(limit=1)
        else: await ctx.channel.send(f'иди нахуй {ctx.author.name}')

    @commands.command(name="move")
    async def move(self, ctx, channelpos:int, targets:Greedy[Member]):
        channels = ctx.guild.voice_channels
        if checkRole(self, ctx): 
            for target in targets:
                await target.move_to(channels[channelpos-1])
            await ctx.channel.purge(limit=1)
        else: await ctx.channel.send(f'иди нахуй {ctx.author.name}')

    @commands.command(name="ch")
    async def chnick(self, ctx, member:Member, nick):
        if checkRole(self,ctx): 
            await member.edit(nick=nick)
        await ctx.channel.purge(limit=1)

def checkRole(self, ctx):
        match = False
        role_names = []
        for role in ctx.author.roles:
            role_names.append(role.name)
        for name in role_names:
            if name == 'Дмитрий Антошин' or name == 'ТОВАРИЩ ЛЕНИН':
                match = True
        return match


def setup(bot):
    bot.add_cog(MiscCog(bot))