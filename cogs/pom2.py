import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from helpers.pom_views import InfoView, CharactersView
from helpers.pom_funcs import similarity_sorter, chara_file, best_light_cones, eidolons
from helpers.pom_misc import combat_emojis, path_emojis


class pom2(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    # Character finder command
    @commands.hybrid_command(name="character", description="Search for a specific character.")
    @app_commands.describe(chara_name="Enter the name of the character")
    async def chara_search(self, ctx: commands.Context, *, chara_name: Optional[str]):
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
            skills_embed = discord.Embed(title=f"{chara_info['name']}'s Skills", color=cone_colors[len(chara_info['rarity'])])
            skills_embed.set_thumbnail(url=chara_info['thumb'])
            if chara_skills['basic']['name'] == "":
                skills_embed.add_field(name="Skills not found", value=f"Information regarding {chara_info['name']}'s skills is not out yet :(")
            else:
                skills_embed.add_field(name="__Basic ATK__", value=f"**Name:** *{chara_skills['basic']['name']}*\n**Tag:** {chara_skills['basic']['tag']}\n**Description:** {chara_skills['basic']['description']}", inline=False)
                for x in range(2, 5):
                    basic = f'basic{x}'
                    try:
                        skills_embed.add_field(name=f"__Basic ATK {x}__", value=f"**Name:** *{chara_skills[basic]['name']}*\n**Tag:** {chara_skills[basic]['tag']}\n**Description:** {chara_skills[basic]['description']}", inline=False)
                    except KeyError:
                        break
                skills_embed.add_field(name="__Skill__", value=f"**Name:** *{chara_skills['skill']['name']}*\n**Tag:** {chara_skills['skill']['tag']}\n**Description:** {chara_skills['skill']['description']}", inline=False)
                skills_embed.add_field(name="__Ultimate__", value=f"**Name:** *{chara_skills['ult']['name']}*\n**Tag:** {chara_skills['ult']['tag']}\n**Description:** {chara_skills['ult']['description']}", inline=False)
                skills_embed.add_field(name="__Talent__", value=f"**Name:** *{chara_skills['talent']['name']}*\n**Tag:** {chara_skills['talent']['tag']}\n**Description:** {chara_skills['talent']['description']}", inline=False)
                skills_embed.add_field(name="__Technique__", value=f"**Name:** *{chara_skills['technique']['name']}*\n**Description:** {chara_skills['technique']['description']}", inline=False)

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

            # Eidelons embed below
            eidolons_details = [eidolon for eidolon in eidolons if eidolon['character'] == result]
            thumb = [chara['thumb'] for chara in chara_file if chara['name'] == result][0]
            if eidolons_details != []:
                eidolons_details = eidolons_details[0]
                eidolon_embed = discord.Embed(title=f"{result}'s Eidolons", color=cone_colors[len(chara_info['rarity'])])
                for num in range(1, 7):
                    eidolon = eidolons_details[f'e{num}']
                    eidolon_embed.add_field(name=f"E{num} - {eidolon['name']}", value=f"*{eidolon['description']}*", inline=False)
            else:
                eidolon_embed = discord.Embed(title=f"{result}'s Eidolons", description=f"Details regarding {result}'s Eidolons is not out yet.", color=cone_colors[len(chara_info['rarity'])])
            eidolon_embed.set_thumbnail(url=thumb)

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

        chara_info = [each for each in chara_file if each['name'] == result][0]
        chara_skills = [each['skills'] for each in chara_file if each['name'] == result][0]

        cone_colors = {5: 0x0062cc, 7: 0xa000c8, 9: 0xedcb01}
        skills_embed = discord.Embed(title=f"{chara_info['name']}", color=cone_colors[len(chara_info['rarity'])])
        skills_embed.set_thumbnail(url=chara_info['thumb'])
        if chara_skills['basic']['name'] == "":
            skills_embed.add_field(name="Skills not found", value="Information regarding this character's skills is not out yet :(")
        else:
            skills_embed.add_field(name="__Basic ATK__", value=f"**Name:** *{chara_skills['basic']['name']}*\n**Tag:** {chara_skills['basic']['tag']}\n**Description:** {chara_skills['basic']['description']}", inline=False)
            for x in range(2, 5):
                basic = f'basic{x}'
                try:
                    skills_embed.add_field(name=f"__Basic ATK {x}__", value=f"**Name:** *{chara_skills[basic]['name']}*\n**Tag:** {chara_skills[basic]['tag']}\n**Description:** {chara_skills[basic]['description']}", inline=False)
                except KeyError:
                    break
            skills_embed.add_field(name="__Skill__", value=f"**Name:** *{chara_skills['skill']['name']}*\n**Tag:** {chara_skills['skill']['tag']}\n**Description:** {chara_skills['skill']['description']}", inline=False)
            skills_embed.add_field(name="__Ultimate__", value=f"**Name:** *{chara_skills['ult']['name']}*\n**Tag:** {chara_skills['ult']['tag']}\n**Description:** {chara_skills['ult']['description']}", inline=False)
            skills_embed.add_field(name="__Talent__", value=f"**Name:** *{chara_skills['talent']['name']}*\n**Tag:** {chara_skills['talent']['tag']}\n**Description:** {chara_skills['talent']['description']}", inline=False)
            skills_embed.add_field(name="__Technique__", value=f"**Name:** *{chara_skills['technique']['name']}*\n**Description:** {chara_skills['technique']['description']}", inline=False)

        await ctx.send(embed=skills_embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(pom2(client))
