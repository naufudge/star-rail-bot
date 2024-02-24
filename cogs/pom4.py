import discord
from discord import app_commands
from discord.ext import commands
from helpers.pom_funcs import similarity_sorter, chara_file
from helpers.pom_embeds import PomPomEmbeds


class pom4(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    # Eidolons command
    @commands.hybrid_command(name="eidolons", description="Gives you the Eidolons of a specific character.")
    @app_commands.describe(character_name="Enter the name of the character")
    async def eidolons_search(self, ctx: commands.Context, *, character_name: str):
        available_charas = [each['name'] for each in chara_file]
        selected_chara = similarity_sorter(available_charas, character_name)[0]
        pom_embed = PomPomEmbeds(character_name=selected_chara)
        eidolon_embed = pom_embed.Eidolons()

        await ctx.send(embed=eidolon_embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(pom4(client))
