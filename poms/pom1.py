import discord
import random
from discord import app_commands
from discord.ext import commands
from poms.pom_views import HelpView

class pom1(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="help", description="Get help on how to use Pom-Pom")
    async def pp_help(self, interaction: discord.Interaction):
        colors = [0xc71e1e, 0xd83131, 0xc97f7f, 0x9a0000, 0x0f0707]
        help_embed = discord.Embed(title="__Help__", color=random.choice(colors) ,description="Hi Trailblazer! How can Pom-Pom help you today?\n")
        help_embed.add_field(name="``/character <character name>``", value="Gives you some information about a specific character.", inline=False)
        help_embed.add_field(name="``/skills <character name>``", value="Gives you information regarding the skills of a specific character.", inline=False)
        help_embed.add_field(name="``/eidolons <character name>``", value="Lists all the Eidolons of a specific character.", inline=False)
        help_embed.add_field(name="``/light_cone <light cone name>``", value="Gives you information regarding a specific light cone.", inline=False)
        help_embed.add_field(name="``/relics <relic name>``", value="Gives you information regarding a specific relic or planar ornament.", inline=False)
        help_embed.set_footer(text="Made with love by Nauf#0709 :)")
        help_view = HelpView()
        await interaction.response.send_message(embed=help_embed, view=help_view)
        if interaction.guild.id == 782971853999702017:
            await interaction.channel.send(content=f'**{self.client.user.name}** is now on **{len(self.client.guilds)}** servers!')

    @commands.command(name="check")
    @commands.is_owner()
    async def check(self, ctx: commands.Context):
        await ctx.channel.send(f'{self.client.user.name} is now on {len(self.client.guilds)} servers!')

async def setup(client: commands.Bot) -> None:
    await client.add_cog(pom1(client))
