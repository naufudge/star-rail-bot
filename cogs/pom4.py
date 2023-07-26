import discord
from discord import app_commands
from discord.ext import commands
from helpers.pom_funcs import similarity_sorter, eidolons, chara_file


class pom4(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    # Eidolons command
    @commands.hybrid_command(name="eidolons", description="Gives you the Eidolons of a specific character.")
    @app_commands.describe(character_name="Enter the name of the character")
    async def eidolons_search(self, ctx: commands.Context, *, character_name: str):
        available_charas = [each['name'] for each in chara_file]
        selected_chara = similarity_sorter(available_charas, character_name)[0]
        cone_colors = {5: 0x0062cc, 7: 0xa000c8, 9: 0xedcb01}
        results = [eidolon for eidolon in eidolons if eidolon['character'] == selected_chara]
        thumb = [chara['thumb'] for chara in chara_file if chara['name'] == selected_chara][0]
        rarity = [chara['rarity'] for chara in chara_file if chara['name'] == selected_chara][0]

        if results != []:
            results = results[0]
            eidolon_embed = discord.Embed(title=f"{selected_chara}'s Eidolons", color=cone_colors[len(rarity)])
            for num in range(1, 7):
                eidolon = results[f'e{num}']
                eidolon_embed.add_field(name=f"E{num} - {eidolon['name']}", value=f"*{eidolon['description']}*", inline=False)
        else:
            eidolon_embed = discord.Embed(title=f"{selected_chara}'s Eidolons", description=f"Details regarding {selected_chara}'s Eidolons is not out yet.", color=cone_colors[len(rarity)])
        eidolon_embed.set_thumbnail(url=thumb)

        await ctx.send(embed=eidolon_embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(pom4(client))
