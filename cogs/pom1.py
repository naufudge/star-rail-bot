import discord
import random
from discord import app_commands
from discord.ext import commands
from typing import Optional
from cogs.help import CustomHelpCommand

class pom1(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="help", description="Get help on how to use Pom-Pom")
    @app_commands.describe(command_name="Get more information about a specific command")
    async def pp_help(self, interaction: discord.Interaction, command_name: Optional[str] = None):
        custom_help = CustomHelpCommand()
        custom_help.context = ctx = await commands.Context.from_interaction(interaction)
        await custom_help.command_callback(ctx, command = command_name)

    @commands.hybrid_command(name="sync", with_app_command=False, description="syncs the slash commands", hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    async def sync(self, ctx: commands.Context):
        try:
            synced = await self.client.tree.sync()
            await ctx.send(f"{self.client.user.name.capitalize()} has synced {len(synced)} command(s)")
        except Exception as e:
            problem = e.__class__.__name__
            await ctx.send(f"The following error occured; *{problem}*")

    @commands.hybrid_command(name="check", with_app_command=False, description="checks the guild count", hidden=True)
    @commands.is_owner()
    async def check(self, ctx: commands.Context):
        await ctx.send(f'`{self.client.user.name}` is now on **{len(self.client.guilds)}** servers! \n- __Shard Count:__ **{self.client.shard_count}**')

async def setup(client: commands.Bot) -> None:
    await client.add_cog(pom1(client))
