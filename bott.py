import discord
from discord.ext import commands

class PomPomClient(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.presences = True
        intents.message_content = True
        self.poms = ['poms.pom1', 'poms.pom2', 'poms.pom3']

        super().__init__(command_prefix="pom$", intents=intents, help_command=None)

    async def setup_hook(self):
        for ext in self.poms:
            await self.load_extension(ext)

    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord!, and now on {len(self.guilds)} servers!')
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)
        status = discord.Status.online
        await self.change_presence(activity=discord.Game(name="Star Rail ✦"), status=status)
