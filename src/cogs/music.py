from discord.ext import commands
from discord import player, utils, Embed
from discord.ext.commands.core import command
import lavalink
from lavalink import events
import re
url_rx = re.compile(r'https?://(?:www\.)?.+')


class MusicCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.bot.music = lavalink.Client(self.bot.user.id)
        self.bot.music.add_node('localhost',7000,'57500','eu','music-node')
        self.bot.add_listener(self.bot.music.voice_update_handler,'on_socket_response')
        self.bot.music.add_event_hook(self.track_hook)

    async def cog_before_invoke(self, ctx):
        guild_check = ctx.guild is not None

        if guild_check:
            await self.ensure_voice(ctx)

        return guild_check

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)

    async def ensure_voice(self, ctx):
        player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))

        should_connect = ctx.command.name in ('play')

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandInvokeError('Для начала зайди в канал.')

        if not player.is_connected:
            if not should_connect:
                raise commands.CommandInvokeError('Не подключен.')

            player.store('channel', ctx.channel.id)
            await ctx.guild.change_voice_state(channel=ctx.author.voice.channel)
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError('Ты не в том канале.')
        
    @commands.command(name='join')
    async def join(self,ctx):
        print('joined')
        member = utils.find(lambda m: m.id == ctx.author.id, ctx.channel.guild.members)
        print(member)
        if member is not None and member.voice is not None:
            if not player.is_connected:
                player.store('channel',ctx.channel.id)
                await self.connect_to(ctx.guild.id, str(member.voice.channel.id))

    @commands.command(name="play")
    async def play(self,ctx,*,query : str):
        try:
            player = self.bot.music.player_manager.get(ctx.guild.id)

            if not url_rx.match(query):
                query = f'ytsearch:{query}'

                results = await player.node.get_tracks(query)
                tracks = results['tracks'][0:5]
                i = 0 
                query_result = ''
                for track in tracks:
                    i+=1
                    query_result = query_result + f'{i}) {track["info"]["title"]} [{lavalink.format_time(track["info"]["length"])}] - {track["info"]["uri"]}\n'
                embed = Embed()
                embed.description = query_result
                
                await ctx.send(embed=embed)

                def check(m):
                    return m.author.id == ctx.author.id
                
                response = await self.bot.wait_for('message', check = check) 

                track = tracks[int(response.content) - 1]
            else:
                results = await player.node.get_tracks(query)
                track = results['tracks'][0]

            player.add(requester = ctx.author.id, track = track)

            if player.is_playing:
                await ctx.send(f'Композиция {track["info"]["title"]} [{lavalink.format_time(track["info"]["length"])}] добавлена в очередь по просьбе {ctx.author.name}!')

            else: 
                await ctx.send(f'Играет композиция {track["info"]["title"]} [{lavalink.format_time(track["info"]["length"])}] по просьбе {ctx.author.name}')
                await player.play()
        
        except Exception as error:
            await ctx.send(error)

    @commands.command(name="pause")
    async def pause(self,ctx):

        player = self.bot.music.player_manager.get(ctx.guild.id)
        await self.ensure_voice(ctx)
        
        await player.set_pause(True)
    @commands.command(name="unpause")
    async def unpause(self,ctx):

        player = self.bot.music.player_manager.get(ctx.guild.id)
        await self.ensure_voice(ctx)
        
        await player.set_pause(False)

    @commands.command(name="stop")
    async def stop(self,ctx):

        player = self.bot.music.player_manager.get(ctx.guild.id)
        await self.ensure_voice(ctx)
        await ctx.send(f'Вечеринка окончена по просьбе {ctx.author.name}...')
        player.queue.clear()
        await player.stop()
        await ctx.guild.change_voice_state(channel=None)

    @commands.command(name="skip")
    async def skip(self,ctx):

        player = self.bot.music.player_manager.get(ctx.guild.id)
        await self.ensure_voice(ctx)
        await ctx.send(f'Скипаем трек по просьбе {ctx.author.name}.')
        await player.skip()

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)
    
    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id),channel_id)
    


def setup(bot):
    bot.add_cog(MusicCog(bot))