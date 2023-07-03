import discord
import os
from discord.ext import commands, tasks
from discord.ext.commands import errors
from concurrent.futures import ThreadPoolExecutor
import topgg

class PomPomClient(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        # REMEMBER TO CHANGE THE INTENTS BEFORE FINALING
        intents = discord.Intents.default()
        # intents.message_content = True
        super().__init__(**kwargs, command_prefix=commands.when_mentioned_or('pom$'), intents=intents, help_command=None)
        self.activity = discord.Game(name="/warp | Star Rail ✦")
        self.topggpy = topgg.DBLClient(self, kwargs['topgg_token'])
        # self.executor = ThreadPoolExecutor()

    # Because I seperated your cogs into a cog folder, we can just iterate over the folder instead of having to hard-code cog names with self.poms
    async def setup_hook(self):
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
        else:
            # report_channel = self.get_channel(id=1123923664941883422)
            # embed = discord.Embed(title='An Error has occurred', description=f'Error: \n `{error}`', timestamp=ctx.message.created_at, color=0x242424)
            # await report_channel.send(embed=embed)
            print(error)

    @tasks.loop(hours=12)
    async def update_stats(self):
        try:
            await self.topggpy.post_guild_count()
            print(f'Posted server count ({self.topggpy.guild_count})')
        except Exception as e:
            print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

    async def on_ready(self):
        # You can use a logger here instead of printing: https://discordpy.readthedocs.io/en/stable/logging.html
        # The logger can be used globally through self.client.log.info("some string here")
        print(f'{self.user.name} has connected to Discord!, and now on {len(self.guilds)} servers!')
        self.update_stats.start()

