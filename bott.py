from typing import List
import discord, random, json, httpx
from discord import app_commands
from discord.ext import commands
from difflib import SequenceMatcher

with open('characters.json', 'r') as f:
    chara_file = json.load(f)

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

    # character finder
    @client.tree.command(name="character", description="Gives you some information about a specific character.")
    @app_commands.describe(chara_name="Enter the name of the character")
    async def chara_search(interaction: discord.Interaction, chara_name: str):
        names = [x['name'] for x in chara_file]
        result = similarity_sorter(names, chara_name)[0] # finds the character name most similar to the search
        # await interaction.response.defer()
        for each in chara_file:
            if each['name'] == result:
                chara_info = each
                try:
                    chara_skills = chara_info['skills']
                except KeyError:
                    pass

        colors = [0xb0bf1a, 0xc9ffe5, 0xb284be]
        # Character information embed below
        info_embed = discord.Embed(title=f"__{chara_info['name']}__", color=random.choice(colors))
        info_embed.set_thumbnail(url=chara_info['thumb'])
        try:
            info_embed.add_field(name="Rarity:", value=f"{str(chara_info['rarity'])}", inline=False)
        except:
            pass
        info_embed.add_field(name="Description:", value=f"{str(chara_info['description'])}", inline=False)
        info_embed.add_field(name="Path:", value=f"*{str(chara_info['path'])}*", inline=True)
        info_embed.add_field(name="Combat Type:", value=f"*{str(chara_info['combat'])}*", inline=True)
        info_embed.add_field(name="Faction:", value=f"*{str(chara_info['faction'])}*", inline=False)
        info_embed.set_image(url=chara_info['picture'])

        # Character Skills embed below
        skills_embed = discord.Embed(title=f"{chara_info['name']}", color=random.choice(colors))
        skills_embed.set_thumbnail(url=chara_info['thumb'])
        try:
            skills_embed.add_field(name="__Basic ATK__", value=f"**Name:** *{chara_skills['basic']['name']}*\n **Tag:** {chara_skills['basic']['tag']}\n **Description:** {chara_skills['basic']['description']}", inline=False)
            skills_embed.add_field(name="__Skill__", value=f"**Name:** *{chara_skills['skill']['name']}*\n **Tag:** {chara_skills['skill']['tag']}\n **Description:** {chara_skills['skill']['description']}", inline=False)
            skills_embed.add_field(name="__Ultimate__", value=f"**Name:** *{chara_skills['ult']['name']}*\n **Tag:** {chara_skills['ult']['tag']}\n **Description:** {chara_skills['ult']['description']}", inline=False)
            skills_embed.add_field(name="__Talent__", value=f"**Name:** *{chara_skills['talent']['name']}*\n **Tag:** {chara_skills['talent']['tag']}\n **Description:** {chara_skills['talent']['description']}", inline=False)
            skills_embed.add_field(name="__Technique__", value=f"**Name:** *{chara_skills['technique']['name']}*\n **Tag:** {chara_skills['technique']['tag']}\n **Description:** {chara_skills['technique']['description']}", inline=False)
        except:
            pass
        embeds = [info_embed, skills_embed]

        info_view = InfoView(embeds)
        await interaction.response.send_message(embed=info_view.initial, view=info_view)

    # character SKILLS
    @client.tree.command(name="skills", description="Gives you the information regarding the skills of a specific character.")
    @app_commands.describe(chara_name="Enter the name of the character")
    async def skill_search(interaction: discord.Interaction, chara_name: str):
        names = [x['name'] for x in chara_file]
        result = similarity_sorter(names, chara_name)[0] # finds the character name most similar to the search

        for each in chara_file:
            if each['name'] == result:
                chara_info = each
                chara_skills = chara_info['skills']

        colors = [0xb0bf1a, 0xc9ffe5, 0xb284be]
        skills_embed = discord.Embed(title=f"{chara_info['name']}", color=random.choice(colors))
        skills_embed.set_thumbnail(url=chara_info['thumb'])
        skills_embed.add_field(name="__Basic ATK__", value=f"**Name:** *{chara_skills['basic']['name']}*\n **Tag:** {chara_skills['basic']['tag']}\n **Description:** {chara_skills['basic']['description']}", inline=False)
        skills_embed.add_field(name="__Skill__", value=f"**Name:** *{chara_skills['skill']['name']}*\n **Tag:** {chara_skills['skill']['tag']}\n **Description:** {chara_skills['skill']['description']}", inline=False)
        skills_embed.add_field(name="__Ultimate__", value=f"**Name:** *{chara_skills['ult']['name']}*\n **Tag:** {chara_skills['ult']['tag']}\n **Description:** {chara_skills['ult']['description']}", inline=False)
        skills_embed.add_field(name="__Talent__", value=f"**Name:** *{chara_skills['talent']['name']}*\n **Tag:** {chara_skills['talent']['tag']}\n **Description:** {chara_skills['talent']['description']}", inline=False)
        skills_embed.add_field(name="__Technique__", value=f"**Name:** *{chara_skills['technique']['name']}*\n **Tag:** {chara_skills['technique']['tag']}\n **Description:** {chara_skills['technique']['description']}", inline=False)

        await interaction.response.send_message(embed=skills_embed)


    @client.tree.command(name="hello")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(f"<:smile:1032884011523129344>")
        # await interaction.response.send_message(f"Goodbye {interaction.user.mention}!")


    @client.event
    async def on_ready():
        print(f'{client.user.name} has connected to Discord!')

        try:
            synced = await client.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

        status = discord.Status.idle
        await client.change_presence(activity=discord.Game(name="Star Rail ✦"), status=status)

    client.run(TOKEN)
