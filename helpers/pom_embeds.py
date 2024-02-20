from discord import Embed
from helpers.pom_misc import combat_emojis, path_emojis
from helpers.pom_funcs import chara_file, eidolons

CONE_COLORS = {5: 0x0062cc, 7: 0xa000c8, 9: 0xedcb01}

class PomPomEmbeds:
    def __init__(self, character_name: str):
        self.result = character_name
        self.chara_info: dict = [each for each in chara_file if each['name'] == character_name][0]

    def CharaInfo(self):
        """Returns embed with the basic information of the character."""
        info_embed = Embed(title=f"__{self.chara_info['name']}__", description=f"{str(self.chara_info['description'])}", color=CONE_COLORS[len(self.chara_info['rarity'])])
        info_embed.set_thumbnail(url=self.chara_info['thumb'])
        info_embed.add_field(name="Rarity:", value=f"{str(self.chara_info['rarity'])}", inline=False)
        combat_type = str(self.chara_info['combat'])
        info_embed.add_field(name="Combat Type:", value=f"*{combat_type} {combat_emojis[combat_type]}*", inline=True)
        path = str(self.chara_info['path'])
        info_embed.add_field(name="Path:", value=f"*{path} {path_emojis[path]}*", inline=True)
        info_embed.add_field(name="Faction:", value=f"*{str(self.chara_info['faction'])}*", inline=False)
        info_embed.set_image(url=self.chara_info['picture'])

        return info_embed

    def Skills(self):
        """Returns the skills embed for the given character."""
        skills_embed = Embed(title=f"{self.chara_info['name']}'s Skills", color=CONE_COLORS[len(self.chara_info['rarity'])])
        skills_embed.set_thumbnail(url=self.chara_info['thumb'])
        chara_skills = self.chara_info['skills']

        if chara_skills['basic']['name'] == "":
            skills_embed.add_field(name="Skills not found", value=f"Information regarding {self.chara_info['name']}'s skills is not out yet :(")
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

        return skills_embed
    
    def Eidolons(self):
        """Returns embed with the character's Eidolons."""
        eidolons_details = [eidolon for eidolon in eidolons if eidolon['character'] == self.result]
        thumb = self.chara_info['thumb']
        # thumb = [chara['thumb'] for chara in chara_file if chara['name'] == result][0]
        if eidolons_details != []:
            eidolons_details = eidolons_details[0]
            eidolon_embed = Embed(title=f"{self.result}'s Eidolons", color=CONE_COLORS[len(self.chara_info['rarity'])])
            for num in range(1, 7):
                eidolon = eidolons_details[f'e{num}']
                eidolon_embed.add_field(
                    name=f"E{num} - {eidolon['name']}",
                    value=f"*{eidolon['description']}*",
                    inline=False
                )
        else:
            eidolon_embed = Embed(
                title=f"{self.result}'s Eidolons",
                description=f"Details regarding {self.result}'s Eidolons is not out yet.",
                color=CONE_COLORS[len(self.chara_info['rarity'])]
            )
        eidolon_embed.set_thumbnail(url=thumb)

        return eidolon_embed