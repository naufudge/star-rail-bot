import discord
from discord import app_commands
from discord.ext import commands
import json
from io import BytesIO
from warps.inventory_view import inventory_view

class pom6(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="my_characters", description="View all the characters you own.")
    async def my_charas(self, interaction: discord.Interaction):
        with open('warps/data/user_data.json', 'r') as f:
            user_data = json.load(f)
            
        selected_user = user_data[str(interaction.user.id)]
        result = inventory_view(selected_user)

        middle_man = BytesIO()
        result.save(middle_man, format="PNG", optimize=True)
        middle_man.seek(0)
        file = discord.File(middle_man, filename="charas.png")

        my_charas_embed = discord.Embed(title=f"{interaction.user.name}'s Characters", color=0xffffff)
        my_charas_embed.set_image(url="attachment://charas.png")

        await interaction.response.send_message(file=file, embed=my_charas_embed)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(pom6(client))
