from discord.ext import commands
from discord import player, utils
import lavalink
from lavalink import events


class MusicCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.bot.music = lavalink.Client(self.bot.user.id)
        self.bot.music.add_node('localhost',7000,'57500','eu','music-node')
        self.bot.add_listener(self.bot.music.voice_update_handler,'on_socket_response')
        self.bot.music.add_event_hook(self.track_hook)


    @commands.command(name='join')
    async def join(self,ctx):
        print('joined')
        member = utils.find(lambda m: m.id == ctx.author.id, ctx.channel.guild.members)
        print(member)
        if member is not None and member.voice is not None:
            player = self.bot.music.player_manager.create(ctx.guild.id,endpoint = str(ctx.guild.region))
            if not player.is_connected:
                player.store('channel',ctx.channel.id)
                await self.connect_to(ctx.guild.id, str(member.voice.channel.id))
        
    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)
    
    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id),channel_id)



def setup(bot):
    bot.add_cog(MusicCog(bot))