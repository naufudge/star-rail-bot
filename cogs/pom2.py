import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from helpers.pom_views import InfoView, CharactersView
from helpers.pom_funcs import similarity_sorter, chara_file, best_light_cones, eidolons
from helpers.pom_misc import combat_emojis, path_emojis
from helpers.pom_embeds import SkillsEmbed, PomPomEmbeds


class pom2(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    # Character finder command
    @commands.hybrid_command(name="character", description="Search for a specific character.")
    @app_commands.describe(chara_name="Enter the name of the character")
    async def chara_search(self, ctx: commands.Context, *, chara_name: Optional[str]):
        if chara_name:
            names = [x['name'] for x in chara_file]
            result: str = similarity_sorter(names, chara_name)[0] # Finds the name most similar to the search
            pom_embeds = PomPomEmbeds(character_name=result)
            chara_info = [each for each in chara_file if each['name'] == result][0]

            cone_colors = {5: 0x0062cc, 7: 0xa000c8, 9: 0xedcb01}
            # Character information embed below
            info_embed = pom_embeds.CharaInfo()

            # Character Skills embed below
            skills_embed = pom_embeds.Skills()

            # Best Light Cones embed below
            try:
                best_cone_details = best_light_cones[result]
                best_cone_names = best_cone_details['light_cones']
                best_cone_embed = discord.Embed(title=f"Best Light Cones for {chara_info['name']}", description='\n'.join(best_cone_names), color=cone_colors[len(chara_info['rarity'])])
                if best_cone_details['credit']:
                    best_cone_embed.set_footer(text=f"All credits to {best_cone_details['credit']}")
            except KeyError:
                best_cone_names = None
                best_cone_embed = discord.Embed(title="Sorry! Work in progress :(", description="We're still working on this, come back again later Trailblazer.", color=cone_colors[len(chara_info['rarity'])])
            best_cone_embed.set_thumbnail(url=chara_info['thumb'])

            # Eidolons embed below
            eidolon_embed = pom_embeds.Eidolons()

            main_embeds = [info_embed, skills_embed, eidolon_embed, best_cone_embed]
            info_view = InfoView(main_embeds, best_cone_names)
            await ctx.send(embed=info_view.initial, view=info_view)
        else:
            emb = discord.Embed(title="Characters", description="Find any playable/announced character under their respective paths", color=0xffffff)
            charas_view = CharactersView()
            
            await ctx.send(embed=emb, view=charas_view)

    # Character skills command
    @commands.hybrid_command(name="skills", description="Gives you information regarding the skills of a specific character.")
    @app_commands.describe(chara_name="Enter the name of the character")
    async def skill_search(self, ctx: commands.Context, *, chara_name: str):
        names = [x['name'] for x in chara_file]
        result = similarity_sorter(names, chara_name)[0] # finds the name most similar to the search

        skills_embed = SkillsEmbed(character_name=result)
        await ctx.send(embed=skills_embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(pom2(client))
