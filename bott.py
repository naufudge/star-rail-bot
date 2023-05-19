from typing import List, Optional
import discord, random, json, httpx
from discord import app_commands
from discord.ext import commands
from difflib import SequenceMatcher

with open('data/characters.json', 'r') as f:
    chara_file = json.load(f)
with open('data/light_cones.json', 'r') as f:
    light_cones = json.load(f)

def similar(a, b):
    """
    Similarity check between ``a`` and ``b``. Returns a ratio (Float).
    """
    return SequenceMatcher(None, a, b).ratio()

def similarity_sorter(search_results, keyword):
    """
    Sorts the search results based on the similarity between it and the keyword.
    ### Parameters
    ``search_results``: sequence
        A non-empty sequence of search results. \n
    ``keyword``: str
        The name of the manga you searched. \n
    Returns the sorted list.
    """
    temp_listed_results = []
    for result in search_results:
        x = similar(keyword, result)
        temp_listed_results.append((x, result))

    temp_listed_results.sort(reverse=True)
    sorted_results = [x[1] for x in temp_listed_results]

    return sorted_results

intents = discord.Intents.default()
intents.presences = True
intents.message_content = True

class InfoView(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed]):
        super().__init__(timeout=None)
        self._embeds = embeds
        self._initial = embeds[0]

    @discord.ui.select(
        placeholder="Choose an option",
        options=[
            discord.SelectOption(label="Character Information", value="1", description="Displays general information of a character"),
            discord.SelectOption(label="Character Skills", value="2", description="Displays information of character's skills")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        select.disabled = False
        if select.values[0] == "1":
            await interaction.response.edit_message(embed=self._embeds[0])
        elif select.values[0] == "2":
            await interaction.response.edit_message(embed=self._embeds[1])

    @property
    def initial(self) -> discord.Embed:
        return self._initial

def run_discord_bot():
    with open('config.json', 'r') as f:
        config = json.load(f)

    TOKEN = config['TOKEN']
    client = commands.Bot(command_prefix='$', intents=intents, help_command=None)

    # Help Command
    @client.tree.command(name="help", description="Get help on how to use Pom-Pom")
    async def pp_help(interaction: discord.Interaction):
        colors = [0xc71e1e, 0xd83131, 0xc97f7f, 0x9a0000, 0x0f0707]
        help_embed = discord.Embed(title="__Help__", color=random.choice(colors) ,description="Hi Trailblazer! How can Pom-Pom help you today?\n")
        help_embed.add_field(name="``/character <character name>``", value="Gives you some information about a specific character.", inline=False)
        help_embed.add_field(name="``/skills <character name>``", value="Gives you information regarding the skills of a specific character.", inline=False)
        help_embed.add_field(name="``/light_cone <light cone name>``", value="Gives you information regarding a specific light cone.", inline=False)
        help_embed.set_footer(text="Made with love by Nauf#0709 :)")
        await interaction.response.send_message(embed=help_embed)

    # Character finder command
    @client.tree.command(name="character", description="Gives you some information about a specific character.")
    @app_commands.describe(chara_name="Enter the name of the character")
    async def chara_search(interaction: discord.Interaction, chara_name: str):
        names = [x['name'] for x in chara_file]
        result = similarity_sorter(names, chara_name)[0] # Finds the name most similar to the search
        for each in chara_file:
            if each['name'] == result:
                chara_info = each
                try:
                    chara_skills = chara_info['skills']
                except KeyError:
                    print("Character skills not found")

        cone_colors = {5: 0x0062cc, 7: 0xa000c8, 9: 0xedcb01}
        # Character information embed below
        info_embed = discord.Embed(title=f"__{chara_info['name']}__", description=f"{str(chara_info['description'])}", color=cone_colors[len(chara_info['rarity'])])
        info_embed.set_thumbnail(url=chara_info['thumb'])
        info_embed.add_field(name="Rarity:", value=f"{str(chara_info['rarity'])}", inline=False)
        # info_embed.add_field(name="Description:", value=f"{str(chara_info['description'])}", inline=False)
        info_embed.add_field(name="Combat Type:", value=f"*{str(chara_info['combat'])}*", inline=True)
        info_embed.add_field(name="Path:", value=f"*{str(chara_info['path'])}*", inline=True)
        info_embed.add_field(name="Faction:", value=f"*{str(chara_info['faction'])}*", inline=False)
        info_embed.set_image(url=chara_info['picture'])

        # Character Skills embed below
        skills_embed = discord.Embed(title=f"{chara_info['name']}", color=cone_colors[len(chara_info['rarity'])])
        skills_embed.set_thumbnail(url=chara_info['thumb'])
        if chara_skills['basic']['name'] == "":
            skills_embed.add_field(name="Skills not found", value=f"Information regarding {chara_info['name']}'s skills is not out yet :(")
        else:
            skills_embed.add_field(name="__Basic ATK__", value=f"**Name:** *{chara_skills['basic']['name']}*\n**Tag:** {chara_skills['basic']['tag']}\n**Description:** {chara_skills['basic']['description']}", inline=False)
            skills_embed.add_field(name="__Skill__", value=f"**Name:** *{chara_skills['skill']['name']}*\n**Tag:** {chara_skills['skill']['tag']}\n**Description:** {chara_skills['skill']['description']}", inline=False)
            skills_embed.add_field(name="__Ultimate__", value=f"**Name:** *{chara_skills['ult']['name']}*\n**Tag:** {chara_skills['ult']['tag']}\n**Description:** {chara_skills['ult']['description']}", inline=False)
            skills_embed.add_field(name="__Talent__", value=f"**Name:** *{chara_skills['talent']['name']}*\n**Tag:** {chara_skills['talent']['tag']}\n **Description:** {chara_skills['talent']['description']}", inline=False)
            skills_embed.add_field(name="__Technique__", value=f"**Name:** *{chara_skills['technique']['name']}*\n**Tag:** {chara_skills['technique']['tag']}\n**Description:** {chara_skills['technique']['description']}", inline=False)

        embeds = [info_embed, skills_embed]

        info_view = InfoView(embeds)
        await interaction.response.send_message(embed=info_view.initial, view=info_view)

    # Character skills command
    @client.tree.command(name="skills", description="Gives you the information regarding the skills of a specific character.")
    @app_commands.describe(chara_name="Enter the name of the character")
    async def skill_search(interaction: discord.Interaction, chara_name: str):
        names = [x['name'] for x in chara_file]
        result = similarity_sorter(names, chara_name)[0] # finds the name most similar to the search

        for each in chara_file:
            if each['name'] == result:
                chara_info = each
                chara_skills = chara_info['skills']

        cone_colors = {5: 0x0062cc, 7: 0xa000c8, 9: 0xedcb01}
        skills_embed = discord.Embed(title=f"{chara_info['name']}", color=cone_colors[len(chara_info['rarity'])])
        skills_embed.set_thumbnail(url=chara_info['thumb'])
        if chara_skills['basic']['name'] == "":
            skills_embed.add_field(name="Skills not found", value="Information regarding this character's skills is not out yet :(")
        else:
            skills_embed.add_field(name="__Basic ATK__", value=f"**Name:** *{chara_skills['basic']['name']}*\n**Tag:** {chara_skills['basic']['tag']}\n**Description:** {chara_skills['basic']['description']}", inline=False)
            skills_embed.add_field(name="__Skill__", value=f"**Name:** *{chara_skills['skill']['name']}*\n**Tag:** {chara_skills['skill']['tag']}\n**Description:** {chara_skills['skill']['description']}", inline=False)
            skills_embed.add_field(name="__Ultimate__", value=f"**Name:** *{chara_skills['ult']['name']}*\n**Tag:** {chara_skills['ult']['tag']}\n**Description:** {chara_skills['ult']['description']}", inline=False)
            skills_embed.add_field(name="__Talent__", value=f"**Name:** *{chara_skills['talent']['name']}*\n**Tag:** {chara_skills['talent']['tag']}\n**Description:** {chara_skills['talent']['description']}", inline=False)
            skills_embed.add_field(name="__Technique__", value=f"**Name:** *{chara_skills['technique']['name']}*\n**Tag:** {chara_skills['technique']['tag']}\n**Description:** {chara_skills['technique']['description']}", inline=False)

        await interaction.response.send_message(embed=skills_embed)

    @client.tree.command(name="light_cone", description="Look up any light cone you want")
    @app_commands.describe(name="Enter the name of the light cone")
    async def light_cones_info(interaction: discord.Interaction, name: Optional[str]):
        cone_names = [x['name'] for x in light_cones]
        colors = [0xc71e1e, 0xd83131, 0xc97f7f, 0x9a0000, 0x0f0707]
        if name:
            result = similarity_sorter(cone_names, name)[0]
            for each in light_cones:
                if each['name'] == result:
                    light_cone = each

            cone_colors = {5: 0x0062cc, 7: 0xa000c8, 9: 0xedcb01}
            cone_embed = discord.Embed(title=light_cone['name'], description=f"*{light_cone['description']}*", color=cone_colors[len(light_cone['rarity'])])
            cone_embed.set_thumbnail(url=light_cone['thumb'])
            cone_embed.set_image(url=light_cone['picture'])
            cone_embed.add_field(name="Path", value=light_cone['path'])
            cone_embed.add_field(name="Rarity", value=light_cone['rarity'])
            cone_embed.add_field(name="Effect", value=light_cone['effect'], inline=False)
            cone_embed.set_footer(text="If this isn't the light cone you are looking for, use just /light_cone to look up all light cones!")
            await interaction.response.send_message(embed=cone_embed)
        else:
            emb = discord.Embed(title="Light Cones", description="Lookup any light cone from below", color=random.choice(colors))
            emb.add_field(name="Available light cones", value=', '.join(cone_names[0:26]))
            emb.set_footer(text="This command is under construction!")
            await interaction.response.send_message(embed=emb)


    @client.event
    async def on_ready():
        print(f'{client.user.name} has connected to Discord!')

        try:
            synced = await client.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

        status = discord.Status.online
        await client.change_presence(activity=discord.Game(name="Star Rail ✦"), status=status)

    client.run(TOKEN)
