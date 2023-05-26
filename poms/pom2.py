import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import random
from poms.pom_views import InfoView, CharactersView
from poms.pom_funcs import similarity_sorter, chara_file, best_light_cones
from poms.pom_misc import combat_emojis, path_emojis


class pom2(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    # Character finder command
    @app_commands.command(name="character", description="Search for a specific character.")
    @app_commands.describe(chara_name="Enter the name of the character")
    async def chara_search(self, interaction: discord.Interaction, chara_name: Optional[str]):
        if chara_name:
            names = [x['name'] for x in chara_file]
            result = similarity_sorter(names, chara_name)[0] # Finds the name most similar to the search

            chara_info = [each for each in chara_file if each['name'] == result][0]
            chara_skills = [each['skills'] for each in chara_file if each['name'] == result][0]

            cone_colors = {5: 0x0062cc, 7: 0xa000c8, 9: 0xedcb01}
            # Character information embed below
            info_embed = discord.Embed(title=f"__{chara_info['name']}__", description=f"{str(chara_info['description'])}", color=cone_colors[len(chara_info['rarity'])])
            info_embed.set_thumbnail(url=chara_info['thumb'])
            info_embed.add_field(name="Rarity:", value=f"{str(chara_info['rarity'])}", inline=False)
            combat_type = str(chara_info['combat'])
            info_embed.add_field(name="Combat Type:", value=f"*{combat_type} {combat_emojis[combat_type]}*", inline=True)
            path = str(chara_info['path'])
            info_embed.add_field(name="Path:", value=f"*{path} {path_emojis[path]}*", inline=True)
            info_embed.add_field(name="Faction:", value=f"*{str(chara_info['faction'])}*", inline=False)
            info_embed.set_image(url=chara_info['picture'])

            # Character Skills embed below
            skills_embed = discord.Embed(title=f"{chara_info['name']}", color=cone_colors[len(chara_info['rarity'])])
            skills_embed.set_thumbnail(url=chara_info['thumb'])
            if chara_skills['basic']['name'] == "":
                skills_embed.add_field(name="Skills not found", value=f"Information regarding {chara_info['name']}'s skills is not out yet :(")
            else:
                skills_embed.add_field(name="__Basic ATK__", value=f"**Name:** *{chara_skills['basic']['name']}*\n**Tag:** {chara_skills['basic']['tag']}\n**Description:** {chara_skills['basic']['description']}", inline=False)
                try:
                    skills_embed.add_field(name="__Basic ATK 2__", value=f"**Name:** *{chara_skills['basic2']['name']}*\n**Tag:** {chara_skills['basic2']['tag']}\n**Description:** {chara_skills['basic2']['description']}", inline=False)
                except KeyError:
                    pass
                skills_embed.add_field(name="__Skill__", value=f"**Name:** *{chara_skills['skill']['name']}*\n**Tag:** {chara_skills['skill']['tag']}\n**Description:** {chara_skills['skill']['description']}", inline=False)
                skills_embed.add_field(name="__Ultimate__", value=f"**Name:** *{chara_skills['ult']['name']}*\n**Tag:** {chara_skills['ult']['tag']}\n**Description:** {chara_skills['ult']['description']}", inline=False)
                skills_embed.add_field(name="__Talent__", value=f"**Name:** *{chara_skills['talent']['name']}*\n**Tag:** {chara_skills['talent']['tag']}\n**Description:** {chara_skills['talent']['description']}", inline=False)
                skills_embed.add_field(name="__Technique__", value=f"**Name:** *{chara_skills['technique']['name']}*\n**Tag:** {chara_skills['technique']['tag']}\n**Description:** {chara_skills['technique']['description']}", inline=False)

            # Best Light Cones embed below
            best_cones = [best for best in best_light_cones if best['chara_name'] == chara_info['name']]
            if best_cones != []:
                best_cone_embed = discord.Embed(title=f"Best Light Cones for {chara_info['name']}", description='\n'.join(best_cones[0]['light_cones']), color=cone_colors[len(chara_info['rarity'])])
                best_cone_embed.set_thumbnail(url=chara_info['thumb'])
                best_cone_embed.set_footer(text="All credits to KeqingMains")
                # Getting just the names of the best light cones for the character
                best_cone_names = [best['light_cones'] for best in best_light_cones if best['chara_name'] == chara_info['name']][0]
            else:
                best_cone_names = None
                best_cone_embed = discord.Embed(title="Sorry! Work in progress :(", description="We're still working on this, come back again later Trailblazer.", color=cone_colors[len(chara_info['rarity'])])
                # best_cone_embed.set_image(url=)
            main_embeds = [info_embed, skills_embed, best_cone_embed]

            info_view = InfoView(main_embeds, best_cone_names)
            await interaction.response.send_message(embed=info_view.initial, view=info_view)
        else:
            colors = [0xc71e1e, 0xd83131, 0xc97f7f, 0x9a0000, 0x0f0707]
            emb = discord.Embed(title="Characters", description="Find any playable/announced character under their respective paths", color=random.choice(colors))
            charas_view = CharactersView()
            await interaction.response.send_message(embed=emb, view=charas_view)

    # Character skills command
    @app_commands.command(name="skills", description="Gives you information regarding the skills of a specific character.")
    @app_commands.describe(chara_name="Enter the name of the character")
    async def skill_search(self, interaction: discord.Interaction, chara_name: str):
        names = [x['name'] for x in chara_file]
        result = similarity_sorter(names, chara_name)[0] # finds the name most similar to the search

        chara_info = [each for each in chara_file if each['name'] == result][0]
        chara_skills = [each['skills'] for each in chara_file if each['name'] == result][0]

        cone_colors = {5: 0x0062cc, 7: 0xa000c8, 9: 0xedcb01}
        skills_embed = discord.Embed(title=f"{chara_info['name']}", color=cone_colors[len(chara_info['rarity'])])
        skills_embed.set_thumbnail(url=chara_info['thumb'])
        if chara_skills['basic']['name'] == "":
            skills_embed.add_field(name="Skills not found", value="Information regarding this character's skills is not out yet :(")
        else:
            skills_embed.add_field(name="__Basic ATK__", value=f"**Name:** *{chara_skills['basic']['name']}*\n**Tag:** {chara_skills['basic']['tag']}\n**Description:** {chara_skills['basic']['description']}", inline=False)
            try:
                skills_embed.add_field(name="__Basic ATK 2__", value=f"**Name:** *{chara_skills['basic2']['name']}*\n**Tag:** {chara_skills['basic2']['tag']}\n**Description:** {chara_skills['basic2']['description']}", inline=False)
            except KeyError:
                pass
            skills_embed.add_field(name="__Skill__", value=f"**Name:** *{chara_skills['skill']['name']}*\n**Tag:** {chara_skills['skill']['tag']}\n**Description:** {chara_skills['skill']['description']}", inline=False)
            skills_embed.add_field(name="__Ultimate__", value=f"**Name:** *{chara_skills['ult']['name']}*\n**Tag:** {chara_skills['ult']['tag']}\n**Description:** {chara_skills['ult']['description']}", inline=False)
            skills_embed.add_field(name="__Talent__", value=f"**Name:** *{chara_skills['talent']['name']}*\n**Tag:** {chara_skills['talent']['tag']}\n**Description:** {chara_skills['talent']['description']}", inline=False)
            skills_embed.add_field(name="__Technique__", value=f"**Name:** *{chara_skills['technique']['name']}*\n**Tag:** {chara_skills['technique']['tag']}\n**Description:** {chara_skills['technique']['description']}", inline=False)

        await interaction.response.send_message(embed=skills_embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(pom2(client))
