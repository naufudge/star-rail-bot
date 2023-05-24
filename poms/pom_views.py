import discord
import random
from typing import List
from discord.interactions import Interaction
from poms.pom_funcs import seperate_lcs, similarity_sorter, light_cones


path_emojis = {
    'The Destruction' : '<:destruction:1108984285060407396>',
    'The Abundance' : '<:abundance:1106840945418313808>',
    'The Hunt' : '<:hunt:1108984298977116203>',
    'The Nihility' : '<:nihility:1108984309395763260>',
    'The Erudition' : '<:erudition:1108984287455359109>',
    'The Preservation' : '<:preservation:1108984312969306122>',
    'The Harmony' : '<:harmony:1108984292312358972>'
}

combat_emojis = {
    'Imaginary' : '<:imaginary:1110210127983812688>',
    'Ice' : '<:ice:1110209282286288989>',
    'Quantum' : '<:quantum:1110210137584566403>',
    'Lightning' : '<:lightning:1110210132496875561>',
    'Fire' : '<:firee:1110210125341397112>',
    'Wind' : '<:wind:1110210144169623643>',
    'Physical' : '<:physical:1108984383215513661>'
}

path_and_cones = seperate_lcs(light_cones)


# Views Below
class InfoView(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed], blc: list = None):
        super().__init__(timeout=None)
        self._embeds = embeds
        self._initial = embeds[0]
        self.active = False # checks whether "best light cone" embed is active or not
        if blc != None:
            self.bestlc = BestLcSelect(blc)
        else:
            self.bestlc = None

    @discord.ui.select(
        placeholder="Choose an option",
        options=[
            discord.SelectOption(label="Character Information", value="1", description=None),
            discord.SelectOption(label="Character Skills", value="2", description=None),
            discord.SelectOption(label="Best Light Cones", value="3", description=None)
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        select.disabled = False
        if select.values[0] == "1":
            if self.active == True:
                self.remove_item(self.bestlc)
                await interaction.response.edit_message(embed=self._embeds[0], view=self)
                self.active = False
            else:
                await interaction.response.edit_message(embed=self._embeds[0], view=self)
        elif select.values[0] == "2":
            if self.active == True:
                self.remove_item(self.bestlc)
                await interaction.response.edit_message(embed=self._embeds[1], view=self)
                self.active = False
            else:
                await interaction.response.edit_message(embed=self._embeds[1], view=self)
        elif select.values[0] == "3":
            if self.bestlc != None and self.active == False:
                self.add_item(self.bestlc)
                await interaction.response.edit_message(embed=self._embeds[2], view=self)
                self.active = True
            else:
                await interaction.response.edit_message(embed=self._embeds[2])

    @property
    def initial(self) -> discord.Embed:
        return self._initial

class LightConeSelect(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Choose a Path", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        colors = [0xc71e1e, 0xd83131, 0xc97f7f, 0x9a0000, 0x0f0707]
        cones = "\n".join(path_and_cones[selection])
        new_title = f"Light Cones: {selection} {path_emojis[selection]}"
        emb = discord.Embed(title=new_title, description=cones, color=random.choice(colors))
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