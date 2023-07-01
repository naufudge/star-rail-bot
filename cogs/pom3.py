from typing import Optional
import discord
import random
from discord import app_commands
from discord.ext import commands
from helpers.pom_funcs import similarity_sorter, light_cones, relics
from helpers.pom_views import RelicsView, LightConeView, path_and_cones, path_emojis

class pom3(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    # Light cones command
    @commands.hybrid_command(name="light_cone", description="Look up any light cone you want")
    @app_commands.describe(name="Enter the name of the light cone")
    async def light_cones_info(self, ctx: commands.Context, *, name: Optional[str]):
        cone_names = [x['name'] for x in light_cones]
        colors = [0xc71e1e, 0xd83131, 0xc97f7f, 0x9a0000, 0x0f0707]
        if name:
            result = similarity_sorter(cone_names, name)[0]
            light_cone = [cone for cone in light_cones if cone['name'] == result][0]

            cone_colors = {5: 0x0062cc, 7: 0xa000c8, 9: 0xedcb01}
            cone_embed = discord.Embed(title=light_cone['name'], description=f"*{light_cone['description']}*", color=cone_colors[len(light_cone['rarity'])])
            cone_embed.set_thumbnail(url=light_cone['thumb'])
            cone_embed.set_image(url=light_cone['picture'])
            cone_embed.add_field(name="Path", value=light_cone['path'])
            cone_embed.add_field(name="Rarity", value=light_cone['rarity'])
            if light_cone['source'] != "":
                cone_embed.add_field(name="How to Obtain", value=light_cone['source'], inline=False)
            cone_embed.add_field(name="Effect", value=light_cone['effect'], inline=False)
            cone_embed.set_footer(text="If this isn't the light cone you are looking for, use just /light_cone to look up all light cones!")
            await ctx.send(embed=cone_embed)
        else:
            options = []
            path_list = sorted(list(path_and_cones))
            for path in path_list:
                options.append(
                    discord.SelectOption(label=path, value=path, emoji=path_emojis[path])
                )
            lc_desc = f"Lookup any light cone from any path below. There's currently a total of {len(cone_names)} light cones available in-game!"
            cone_embed = discord.Embed(title="Light Cones", description=lc_desc, color=random.choice(colors))

            light_cone_view = LightConeView(options)
            await ctx.send(embed=cone_embed, view=light_cone_view)

    # Relics command
    @commands.hybrid_command(name="relics", description="Look up any available Relic or Planar Ornament")
    @app_commands.describe(name="Enter the name of a Relic or Planar Ornament")
    async def relics_info(self, ctx: commands.Context, *, name: Optional[str]):
        relics_names = [x['name'] for x in relics]
        colors = [0xc71e1e, 0xd83131, 0xc97f7f, 0x9a0000, 0x0f0707]
        if name:
            result = similarity_sorter(relics_names, name)[0]
            relic_data = [relic for relic in relics if relic['name'] == result][0]
            relic_embed = discord.Embed(title=relic_data['name'], color=random.choice(colors))
            relic_embed.set_thumbnail(url=relic_data['thumb'])
            relic_embed.add_field(name="2 Piece:", value=relic_data['2pc'], inline=False)
            if relic_data['4pc'] != "":
                relic_embed.add_field(name="4 Piece:", value=relic_data['4pc'], inline=False)

            await ctx.send(embed=relic_embed)
        else:
            only_relics = [x['name'] for x in relics if x['type'] == 'Relic']
            only_planar = [x['name'] for x in relics if x['type'] != 'Relic']
            relics_embed = discord.Embed(title="Relics", description="\n".join(sorted(only_relics)), color=random.choice(colors))
            relics_embed.set_footer(text=f"There's currently a total of {len(only_relics)} Relics available in-game")
            planars_embed = discord.Embed(title="Planar Ornaments", description="\n".join(sorted(only_planar)), color=random.choice(colors))
            planars_embed.set_footer(text=f"There's currently a total of {len(only_planar)} Planar Ornaments available in-game")

            options = [relics_embed, planars_embed]
            relic_view = RelicsView(options)

            await ctx.send(embed=relic_view.initial, view=relic_view)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(pom3(client))
