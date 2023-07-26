import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import errors
from motor.motor_asyncio import AsyncIOMotorClient
import os
from warps.inventory_db import uri
# from warps.inventory_db import test_uri


class PomPomClient(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        intents = discord.Intents.default()
        super().__init__(**kwargs, command_prefix=commands.when_mentioned_or('pom$'), intents=intents, help_command=None)
        self.activity = discord.Game(name="/warp | Star Rail ✦")

    async def setup_hook(self):
        try:
            # REMEMBER TO CHANGE THIS WHEN TESTING -------------------------------------
            self.mongoConnect = AsyncIOMotorClient(uri)
            self.user_data_collection = self.mongoConnect['PomPomDB']['characters']
            # self.user_data_collection = self.mongoConnect['PomPomDB']['tester']
        except AttributeError:
            print("Not Connected to PomPomDB :(")

        for filename in [file for file in os.listdir(f'{os.getcwd()}/cogs') if file.lower().endswith('.py')]:
            await self.load_extension(f'cogs.{filename[:-3]}')

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, errors.MissingPermissions):
            await ctx.send(f":x: You can't use that command.", ephemeral=True)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f":x: Required arguments aren't passed.", ephemeral=True)
        elif isinstance(error, errors.CommandNotFound):
            pass
        elif isinstance(error, errors.NotOwner):
            pass
        elif isinstance(error, errors.HybridCommandError) and isinstance(error.original, app_commands.CommandOnCooldown):
            pass
        # elif isinstance(error, errors.HybridCommandError) and isinstance(error.original, app_commands.CommandInvokeError):
        #     pass
        else:
            print(f"{error.__class__.__name__}: {error}")

    async def on_ready(self):
        # You can use a logger here instead of printing: https://discordpy.readthedocs.io/en/stable/logging.html
        # The logger can be used globally through self.client.log.info("some string here")
        print(f'{self.user.name} has connected to Discord!, and now on {len(self.guilds)} servers! \nShard count: {self.shard_count}')

