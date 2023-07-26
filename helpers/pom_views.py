import discord
import random
from typing import List
from discord.interactions import Interaction
from helpers.pom_funcs import seperate_charas, seperate_lcs, similarity_sorter, light_cones, chara_file
from helpers.pom_misc import path_thumbs, path_emojis, combat_emojis,combat_colors


path_and_cones = seperate_lcs(light_cones)
path_and_charas = seperate_charas(chara_file)

# Views Below
class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        vote_btn = discord.ui.Button(label="Vote on Top.gg", url="https://top.gg/bot/1106848782022344765?s=0cca57f4ceea7")
        self.add_item(vote_btn)

class InfoView(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed], blc: list = None):
        super().__init__(timeout=None)
        self._embeds = embeds
        self._initial = embeds[0]
        self.blc_active = False # checks whether "best light cone" embed is active or not
        if blc != None:
            self.bestlc = BestLcSelect(blc)
        else:
            self.bestlc = None

    @discord.ui.select(
        placeholder="Choose an option",
        options=[
            discord.SelectOption(label="Character Information", value="1", description=None),
            discord.SelectOption(label="Character Skills", value="2", description=None),
            discord.SelectOption(label="Eidolons", value="3", description=None),
            discord.SelectOption(label="Best Light Cones", value="4", description=None)
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        select.disabled = False
        if select.values[0] == "1":
            i = 1
            while i < len(self.children):
                self.remove_item(self.children[i])
                i+=1
            self.blc_active = False
            await interaction.response.edit_message(embed=self._embeds[0], view=self)

        elif select.values[0] == "2":
            i = 1
            while i < len(self.children):
                self.remove_item(self.children[i])
                i+=1
            self.blc_active = False
            await interaction.response.edit_message(embed=self._embeds[1], view=self)

        elif select.values[0] == "3":
            i = 1
            while i < len(self.children):
                self.remove_item(self.children[i])
                i+=1
            self.blc_active = False
            await interaction.response.edit_message(embed=self._embeds[2], view=self)

        elif select.values[0] == "4":
            if self.bestlc != None and self.blc_active == False:
                self.add_item(self.bestlc)
                await interaction.response.edit_message(embed=self._embeds[3], view=self)
                self.blc_active = True
            else:
                await interaction.response.edit_message(embed=self._embeds[3])

    @property
    def initial(self) -> discord.Embed:
        return self._initial

class CharactersView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.children[1].disabled = True

    @discord.ui.select(
        placeholder="Select a Path",
        options=[discord.SelectOption(label=path, value=path, emoji=path_emojis[path]) for path in sorted(list(path_and_charas))]
    )
    async def callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.path = select.values[0]
        self.combat = None
        self.children[1].disabled = False
        characters = sorted(path_and_charas[self.path])
        charas_embed = discord.Embed(title=f"Characters: {self.path}", description='\n'.join(characters), color=0xffffff)
        charas_embed.set_thumbnail(url=path_thumbs[self.path])

        await interaction.response.edit_message(embed=charas_embed, view=self)

    @discord.ui.select(
        placeholder="Select an Element",
        options=[discord.SelectOption(label=combat, value=combat, emoji=combat_emojis[combat]) for combat in sorted(list(combat_emojis))]
    )
    async def callback2(self, interaction: discord.Interaction, select: discord.ui.Select):
        if self.path:
            self.combat = select.values[0]
            if self.path != "" and self.combat != "":
                result = [f"{chara['name']} {combat_emojis[chara['combat']]}" for chara in chara_file if (chara['path'] == self.path) and (chara['combat'] == self.combat)]

            if result != []:
                charas_embed = discord.Embed(title=f"Characters: {self.path} + {self.combat}", description='\n'.join(result), color=combat_colors[self.combat])
            else:
                charas_embed = discord.Embed(title=f"Characters: {self.path} + {self.combat}", description="No character of that combination found :(", color=combat_colors[self.combat])
            charas_embed.set_thumbnail(url=path_thumbs[self.path])

            await interaction.response.edit_message(embed=charas_embed, view=self)

class LightConeSelect(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Choose a Path", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        colors = [0xc71e1e, 0xd83131, 0xc97f7f, 0x9a0000, 0x0f0707]
        cones = "\n".join(path_and_cones[selection])
        new_title = f"Light Cones: {selection}"

        emb = discord.Embed(title=new_title, description=cones, color=random.choice(colors))
        emb.set_thumbnail(url=path_thumbs[selection])
        await interaction.response.edit_message(embed=emb)

class LightConeView(discord.ui.View):
    def __init__(self, options):
        super().__init__(timeout=None)
        self.add_item(LightConeSelect(options))

class RelicsView(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed]):
        super().__init__(timeout=None)
        self._embeds = embeds
        self._initial = embeds[0]

    @discord.ui.select(
        placeholder="Choose an option",
        options = [
            discord.SelectOption(label="Relics", value="Relics"),
            discord.SelectOption(label="Planar Ornament", value="Planar Ornament")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == "Relics":
            await interaction.response.edit_message(embed=self._initial)
        elif select.values[0] == "Planar Ornament":
            await interaction.response.edit_message(embed=self._embeds[1])

    @property
    def initial(self) -> discord.Embed:
        return self._initial

class BestLcSelect(discord.ui.Select):
    def __init__(self, best_cones):
        self._bests = best_cones
        options = [discord.SelectOption(label=cone.replace("*", ""), value=cone.replace("*", "")) for cone in self._bests]
        super().__init__(placeholder="Select the Light Cone you want", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: Interaction):
        cone_names = [x['name'] for x in light_cones]
        result = similarity_sorter(cone_names, self.values[0])[0]
        light_cone = [cone for cone in light_cones if cone['name'] == result][0]

        cone_colors = {5: 0x0062cc, 7: 0xa000c8, 9: 0xedcb01}
        cone_embed = discord.Embed(title=light_cone['name'], description=f"*{light_cone['description']}*", color=cone_colors[len(light_cone['rarity'])])
        cone_embed.set_thumbnail(url=light_cone['thumb'])
        cone_embed.set_image(url=light_cone['picture'])
        cone_embed.add_field(name="Path", value=light_cone['path'])
        cone_embed.add_field(name="Rarity", value=light_cone['rarity'])
        cone_embed.add_field(name="Effect", value=light_cone['effect'], inline=False)

        await interaction.response.edit_message(embed=cone_embed)

class LeaderboardsView(discord.ui.View):
    def __init__(self, leaderboards: dict) -> None:
        super().__init__(timeout=None)
        self._leaderboards = leaderboards

    @discord.ui.select(
        placeholder="Choose a leaderboard",
        options = [
            discord.SelectOption(label="5 Stars Leaderboard", value=1),
            discord.SelectOption(label="Ten Pulls Leaderboard", value=2),
            discord.SelectOption(label="Total Characters Leaderboard", value=3),
            discord.SelectOption(label="User Level Leaderboard", value=4)
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        pompom_emoji = "<:Pompom_working:1130937556742197450>"
        if select.values[0] == str(1):
            leaderboard_embed = discord.Embed(title=f"{pompom_emoji} __5 Stars Leaderboard__", description="Top 10 users with the most number of 5 Star character copies", color=0xffffff)
            num = 1
            for username, copies in self._leaderboards['five_stars'].items():
                leaderboard_embed.add_field(
                    name=f"{num}) {username}",
                    value=f"`{[(f'{copy} Copies' if not copy == 1 else f'{copy} Copy') for copy in [copies]][0]}`",
                    inline=False
                    )
                num += 1

        elif select.values[0] == str(2):
            leaderboard_embed = discord.Embed(title=f"{pompom_emoji} __Ten Pulls Leaderboard__", description="Top 10 users who have done the most number of ten pulls", color=0xffffff)
            num = 1
            for username, pulls in self._leaderboards['ten_pulls'].items():
                leaderboard_embed.add_field(name=f"{num}) {username}", value=f"`{pulls} Pulls`", inline=False)
                num += 1

        elif select.values[0] == str(3):
            leaderboard_embed = discord.Embed(title=f"{pompom_emoji} __Total Characters Leaderboard__", description="Top 10 users who have the most number of character copies", color=0xffffff)
            num = 1
            for username, copies in self._leaderboards['total_characters'].items():
                leaderboard_embed.add_field(name=f"{num}) {username}", value=f"`{copies} Copies`", inline=False)
                num += 1

        elif select.values[0] == str(4):
            leaderboard_embed = discord.Embed(title=f"{pompom_emoji} __User Level Leaderboard__", description="Top 10 users with the highest level", color=0xffffff)
            num = 1
            for username, level in self._leaderboards['levels'].items():
                leaderboard_embed.add_field(name=f"{num}) {username}", value=f"`Level {level}`", inline=False)
                num += 1
        else:
            leaderboard_embed = discord.Embed(title="Some error occured")

        leaderboard_embed.set_footer(text=self._leaderboards['update_time'])
        await interaction.response.edit_message(embed=leaderboard_embed, view=self)
