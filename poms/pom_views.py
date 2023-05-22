import discord
import random
import json
from typing import List
from poms.pom_funcs import seperate_lcs

with open('data/light_cones.json', 'r') as f:
    light_cones = json.load(f)

path_emojis = {
    'The Destruction' : '<:destruction:1108984285060407396>',
    'The Abundance' : '<:abundance:1106840945418313808>',
    'The Hunt' : '<:hunt:1108984298977116203>',
    'The Nihility' : '<:nihility:1108984309395763260>',
    'The Erudition' : '<:erudition:1108984287455359109>',
    'The Preservation' : '<:preservation:1108984312969306122>',
    'The Harmony' : '<:harmony:1108984292312358972>'
}

path_and_cones = seperate_lcs(light_cones)


# Views Below
class InfoView(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed]):
        super().__init__(timeout=None)
        self._embeds = embeds
        self._initial = embeds[0]

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
            await interaction.response.edit_message(embed=self._embeds[0])
        elif select.values[0] == "2":
            await interaction.response.edit_message(embed=self._embeds[1])
        elif select.values[0] == "3":
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
        super().__init__()
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
