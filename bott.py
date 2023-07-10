import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import errors
# from concurrent.futures import ThreadPoolExecutor
import topgg
import os
from asyncio import sleep as go_to_sleep

class PomPomClient(commands.AutoShardedBot):
    def __init__(self, topgg_token: str = None, **kwargs):
        intents = discord.Intents.default()
        super().__init__(**kwargs, command_prefix=commands.when_mentioned_or('pom$'), intents=intents, help_command=None)
        self.activity = discord.Game(name="/warp | Star Rail ✦")
        if topgg_token:
            self.topggpy = topgg.DBLClient(self, topgg_token)
        # self.executor = ThreadPoolExecutor()

    async def setup_hook(self):
        try:
            # REMEMBER TO CHANGE THIS WHEN TESTING
            self.user_data_collection = self.mongoConnect['PomPomDB']['characters']
        except AttributeError:
            print("Not Connected to PomPomDB :(")

        self.bg_task = self.loop.create_task(self.update_stats())

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

    async def update_stats(self):
        i = 0
        await self.wait_until_ready()
        try:
            await self.topggpy.post_guild_count()
            i += 1
            if i < 1:
                print(f'Posted server count ({self.topggpy.guild_count})')
        except Exception as e:
            print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))
        await go_to_sleep(60*60)

    async def on_ready(self):
        # You can use a logger here instead of printing: https://discordpy.readthedocs.io/en/stable/logging.html
        # The logger can be used globally through self.client.log.info("some string here")
        print(f'{self.user.name} has connected to Discord!, and now on {len(self.guilds)} servers! \nShard count: {self.shard_count}')

