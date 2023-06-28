import discord
import os
from discord.ext import commands

# I changed your bot class to AutoShardedBot. You will need to shard soon if not immediately
class PomPomClient(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        # REMEMBER TO CHANGE THE INTENTS BEFORE FINALING
        intents = discord.Intents.default()
        # intents.message_content = True
        super().__init__(**kwargs, command_prefix="pom$", intents=intents, help_command=None)

        # You are able to set the status here just by setting self.activity
        self.activity = discord.Game(name="/warp | Star Rail ✦")

    # Because I seperated your cogs into a cog folder, we can just iterate over the folder instead of having to hard-code cog names with self.poms
    async def setup_hook(self):
        for filename in os.listdir(f'{os.getcwd()}/cogs'):
            await self.load_extension(f'cogs.{filename[:-3]}')

    async def on_ready(self):
        # You can use a logger here instead of printing: https://discordpy.readthedocs.io/en/stable/logging.html
        # The logger can be used globally through self.client.log.info("some string here")
        print(f'{self.user.name} has connected to Discord!, and now on {len(self.guilds)} servers!')
        try:
            # If you go to cluster, you will need to avoid syncing your commands this way. It will send too many requests to Discord
            # The recommended way is manually with a command (inconvenient, but if you update command arguments at all you can just
            # sync the tree instead of restarting the entire bot)
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)
