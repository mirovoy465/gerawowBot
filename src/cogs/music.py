from discord.ext import commands
from discord import Embed, Colour
import lavalink
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
        

    @commands.command(name="play",help="Добавить в очередь композицию. Для выбора написать только номер.")
    async def play(self,ctx,*, query : str):

        try:
            player = self.bot.music.player_manager.get(ctx.guild.id)
            # if time: 
            #     time = parse_time(time) 

            if not url_rx.match(query):
                query = f'ytsearch:{query}'

                results = await player.node.get_tracks(query)
                tracks = results['tracks'][0:5]
                i = 0 
                query_result = ''
                for track in tracks:
                    i+=1
                    query_result = query_result + f'{i}) {track["info"]["title"]} [{lavalink.format_time(track["info"]["length"])}] - {track["info"]["uri"]}\n'
                embed = Embed(title="Список треков.",colour=Colour.blue())
                embed.description = query_result
                
                await ctx.send(embed=embed)

                def check(m):
                    return m.author.id == ctx.author.id
                
                response = await self.bot.wait_for('message', check = check) 

                if int(response.content):
                    track = tracks[int(response.content) - 1]
                else:
                    await ctx.channel.purge(limit=3)
                    if not player.queue:
                        await ctx.guild.change_voice_state(channel=None)
                    return

            else:
                results = await player.node.get_tracks(query)
                track = results['tracks'][0]

            player.add(requester = ctx.author.id, track = track)

            await ctx.channel.purge(limit=3)

            if player.is_playing:
                await ctx.send(f'Композиция {track["info"]["title"]} [{lavalink.format_time(track["info"]["length"])}] добавлена в очередь по просьбе {ctx.author.name}!')

            else: 
                await ctx.send(f'Играет композиция {track["info"]["title"]} [{lavalink.format_time(track["info"]["length"])}] по просьбе {ctx.author.name}')
                # await player.play(start_time=time)
                await player.play()
            

        except Exception as error:
            await ctx.send(error)


    @commands.command(name="pause",help="Поставить плеер на паузу.")
    async def pause(self,ctx):

        player = self.bot.music.player_manager.get(ctx.guild.id)
        await self.ensure_voice(ctx)
        
        await player.set_pause(True)


    @commands.command(name="unpause",help="Снять плеер с паузы.")
    async def unpause(self,ctx):

        player = self.bot.music.player_manager.get(ctx.guild.id)
        await self.ensure_voice(ctx)
        
        await player.set_pause(False)


    @commands.command(name="stop",help="Останавливает плеер.")
    async def stop(self,ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        await self.ensure_voice(ctx)
        await ctx.channel.purge(limit=1)
        await ctx.send(f'Вечеринка окончена по просьбе {ctx.author.name}...')
        player.queue.clear()
        await player.stop()
        await ctx.guild.change_voice_state(channel=None)


    @commands.command(name="skip",help="Пропускает трек.")
    async def skip(self,ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        await self.ensure_voice(ctx)
        await ctx.channel.purge(limit=1)
        await ctx.send(f'Скипаем трек по просьбе {ctx.author.name}.')
        await player.skip()


    @commands.command(name="vol",help="Устанавливает громкость (в процентах).")
    async def set_volume(self,ctx, *, vol : float):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        await player.set_volume(vol*10)
        await ctx.channel.purge(limit=1)
        await ctx.send(f'Установлена громкость {vol}%')


    @commands.command(name="eq", help="Эквалайзер.")
    async def eq(self,ctx, *,type : str):
        player = self.bot.music.player_manager.get(ctx.guild.id)

        bass_gain_list = [(0,0.7,),(1,0.7,),(2,0.7,),(3,0.7,),(4,0.7,),(5,0.7)]

        if type == "bass":
            await ctx.channel.purge(limit=1)
            await ctx.send("bass")
            await player.set_gains(*bass_gain_list)
        else:
            await player.reset_equalizer()


    @commands.command(name="fwd", help="Скипнуть к определенному моменту.\nФормат: min:sec")
    async def fwd(self,ctx,*,time):
        player = self.bot.music.player_manager.get(ctx.guild.id)

        await player.seek(parse_time(time))


    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)
    
    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id),channel_id)
    
def parse_time(time_str:str):
    minutes = int(time_str[0:time_str.index(':')])
    seconds = int(time_str[time_str.index(':')+1:])
    return (minutes*60+seconds)*1000

def setup(bot):
    bot.add_cog(MusicCog(bot))