import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from cogs.help import CustomHelpCommand
from helpers.pom_funcs import add_feedback

class pom1(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.user_feedbacks = client.user_feedbacks

    @app_commands.command(name="help", description="Get help on how to use Pom-Pom")
    @app_commands.describe(command_name="Get more information about a specific command")
    async def pp_help(self, interaction: discord.Interaction, command_name: Optional[str] = None):
        custom_help = CustomHelpCommand()
        custom_help.context = ctx = await commands.Context.from_interaction(interaction)
        await custom_help.command_callback(ctx, command = command_name)

    @commands.hybrid_command(name="feedback", description="Provide anonymous feedback or suggestions for Pom-pom's development.")
    @app_commands.describe(msg="Enter anything you would like to tell me.")
    async def feedback(self, ctx: commands.Context, msg: str):
        await add_feedback(self.user_feedbacks, msg)
        feedback_embed = discord.Embed(
            title="Feedback submitted successfully!",
            description="Thank you for the feedback and the constant support for Pom-Pom. It is very much appreciated.",
            color=0xf94449
        )
        await ctx.send(embed=feedback_embed)

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
