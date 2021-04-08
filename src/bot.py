# bot.py
import os
from pathlib import Path
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

class gerawowBot(commands.Bot):

    def __init__(self):
        self._cogs = [p.stem for p in Path(".").glob("./src/cogs/*.py")]
        super().__init__(command_prefix = self.prefix, case_insensetive = True)
    
    def setup(self):
        print("Booting up...")
        for cog in self._cogs:
            self.load_extension(f'src.cogs.{cog}')
            print(f'Loaded cog: {cog}!')

        print("Setup complete!")
    
    def run(self):
        super().run(TOKEN, reconnect = True)

    async def on_connect(self):
        self.setup()
        print(f'{self.user} connected! Latency :{self.latency*1000:,.1f} ms')

    async def on_ready(self):
        print(f'{self.user} ready!')
        self.client_id = (await self.application_info()).id

    async def on_disconnect(self):
        print(f'{self.user} disconnected!')
    
    async def prefix(self,bot,message):
        return commands.when_mentioned_or("gw!")(bot,message)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=commands.Context)
        if ctx.command is not None:
            await self.invoke(ctx)
        
    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)
    
def main():
    bot = gerawowBot()
    bot.run()