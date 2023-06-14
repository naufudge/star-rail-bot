import discord
from discord import app_commands
from discord.ext import commands
from io import BytesIO
import json
import asyncio
# import sqlite3
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from warps.warp import ten_pull
from warps.probabilities import *

with open('warps/standard_banner.json', 'r') as f:
    standard_warps = json.load(f)

class pom5(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.allowed = [782971853999702017, 895415743414427740, 1109045025578430504] # ccomb, dan heng, pom-pom testing
        self.fourstarPity, self.fivestarPity = 1, 1


    @app_commands.command(name="warp", description="Try out your luck in this Warp Simulator! (Beta Ver)")
    @app_commands.describe(warp_name="Choose one of the available Warps")
    @app_commands.choices(warp_name=[
        discord.app_commands.Choice(name="Stellar Warp", value=1)
    ])
    async def wish(self, interaction: discord.Interaction, warp_name: discord.app_commands.Choice[int]):
        if warp_name.value == 1:
            await interaction.response.defer()
            self.three_stars = [chara for chara, deets in standard_warps.items() if deets['rarity'] == 3]
            self.four_stars = [chara for chara, deets in standard_warps.items() if deets['rarity'] == 4]
            self.five_stars = [chara for chara, deets in standard_warps.items() if deets['rarity'] == 5]

            chara_names = list(standard_warps)
            rarities = [standard_warps[chara]['rarity'] for chara in chara_names]
            results = []

            for pull in range(1, 11):
                probability = self.probability_calculator()
                chances = [probability[prob] for prob in rarities]

                self.fourstarPity += 1
                self.fivestarPity += 1
                chara = np.random.choice(chara_names, p=chances)
                results.append(chara)
                if chara in self.four_stars:
                    self.fourstarPity = 1
                if chara in self.five_stars:
                    self.fivestarPity = 1

            with ThreadPoolExecutor() as executor:
                future = executor.submit(self.img_process, results)
                file = future.result()

            if [result for result in results if result in self.five_stars] != []:
                embed_color = 0xedcb01 # 5 star pull
            else:
                embed_color = 0xa000c8 # 4 star pull

            pulls_embed = discord.Embed(title="Warp Simulator", color=embed_color)
            if [result for result in results if result in self.five_stars] != []:
                pulls_embed.set_image(url="https://cdn.discordapp.com/attachments/1117016812069081140/1117017484000772096/five_star.gif")
            else:
                pulls_embed.set_image(url="https://cdn.discordapp.com/attachments/1117016812069081140/1117017472940384317/four_star.gif")
            pulls_embed.set_footer(text="Please do note that this is a prototype and not the final version. There will not be any record of the characters you pull as of now. However, inventory system will be implemented in the near future.")

            await interaction.followup.send(embed=pulls_embed)

            pulls_embed.add_field(name="4 Stars:", value=", ".join(set([result for result in results if result in self.four_stars])), inline=False)
            if [result for result in results if result in self.five_stars] != []:
                pulls_embed.add_field(name="5 Stars:", value=", ".join(set([result for result in results if result in self.five_stars])), inline=False)
            else:
                pulls_embed.add_field(name="5 Stars:", value="--", inline=False)
            pulls_embed.set_image(url="attachment://pulls.png")

            await asyncio.sleep(13)
            await interaction.edit_original_response(attachments=[file], embed=pulls_embed)

    def img_process(self, imgs: list):
        np.random.shuffle(imgs)
        middle_man = BytesIO()
        pulls = ten_pull([f"warps/WarpCards/{result}.png" for result in imgs])
        resized_pulls = pulls.resize(size=(1050,675))
        resized_pulls.save(middle_man, format="PNG", optimize=True)
        middle_man.seek(0)
        file = discord.File(middle_man, filename="pulls.png")
        return file

    def probability_calculator(self):
        # if self.fivestarPity == 90:
        #     probability = {
        #         3 : 0,
        #         4 : 0,
        #         5 : 1/len(self.five_stars)
        #     }

        if self.fourstarPity == 10:
            probability = {
                3 : 0,
                4 : 1/len(self.four_stars),
                5 : 0
            }
        else:
            # five_star_prob = five_star_probabilities[self.fivestarPity]
            five_star_prob = 0.006
            four_star_prob = four_star_probabilities[self.fourstarPity]
            three_star_prob = 1 - (four_star_prob + five_star_prob)
            probability = {
                3 : three_star_prob/len(self.three_stars),
                4 : four_star_prob/len(self.four_stars),
                5 : five_star_prob/len(self.five_stars)
            }
        return probability

async def setup(client: commands.Bot) -> None:
    await client.add_cog(pom5(client))
