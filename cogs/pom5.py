import discord
from discord import app_commands
from discord.ext import commands
from io import BytesIO
import json
import asyncio
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from warps.warp import ten_pull
from warps.probabilities import *

with open('warps/data/standard_banner.json', 'r') as f:
    standard_warps = json.load(f)

class pom5(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.allowed = [782971853999702017, 895415743414427740, 1109045025578430504] # ccomb, dan heng, pom-pom testing
        self.fourstarPity, self.fivestarPity = 1, 1

    @app_commands.checks.cooldown(rate=10, per=120, key=lambda i: (i.user.id))
    @commands.hybrid_command(name="warp", description="Try out your luck in this Warp Simulator!")
    @app_commands.describe(warp_name="Choose one of the available Warps")
    @app_commands.choices(warp_name=[
        discord.app_commands.Choice(name="Stellar Warp", value=1)
    ])
    async def warp(self, ctx: commands.Context, *, warp_name: discord.app_commands.Choice[int]):
        # Standard Banner
        if warp_name.value == 1:
            await ctx.defer()
            self.three_stars = [chara for chara, deets in standard_warps.items() if deets['rarity'] == 3]
            self.four_stars = [chara for chara, deets in standard_warps.items() if deets['rarity'] == 4]
            self.five_stars = [chara for chara, deets in standard_warps.items() if deets['rarity'] == 5]
            # List of 4 & 5 star characters
            self.five_and_four_stars = [chara for chara, deets in standard_warps.items() if (deets['rarity'] == 5 or deets['rarity'] == 4) and (deets['type'] == 'character')]

            pompomParentDB = self.client.mongoConnect['PomPomDB']
            pompomDB = pompomParentDB['characters']
            # ---------------------- PLEASE REMEMBER TO CHANGE THIS (FOR TESTING PURPOSES)-----------------------
            # pompomDB = pompomParentDB['tester']

            user_id = ctx.author.id
            filter = {'_id': user_id}
            if await pompomDB.find_one(filter) == None:
                new_user = {"_id": user_id, "ten_pulls": 0, "characters": {}}
                await pompomDB.insert_one(new_user)
            user_data = await pompomDB.find_one(filter)

            chara_names = list(standard_warps)
            rarities = [standard_warps[chara]['rarity'] for chara in chara_names]
            results = [] # This will contain the characters/weapons that a user gets from the 10 pull

            for pull in range(1, 11):
                probability = self.probability_calculator()
                chances = [probability[rarity] for rarity in rarities]

                self.fourstarPity += 1
                self.fivestarPity += 1
                chara = np.random.choice(chara_names, p=chances)
                results.append(chara)
                if chara in self.four_stars:
                    self.fourstarPity = 1
                if chara in self.five_stars:
                    self.fivestarPity = 1

            list_of_charas_owned = list(user_data["characters"])

            for chara_got in [result for result in results if result in self.five_and_four_stars]:
                if not chara_got in list_of_charas_owned:
                    user_data["characters"][chara_got] = 1
                    list_of_charas_owned.append(chara_got)
                else:
                    user_data["characters"][chara_got] += 1

            updated_ten_pull_count = user_data["ten_pulls"] + 1

            if [result for result in results if result in self.five_and_four_stars] != []:
                updated_post = {"$set": {"ten_pulls": updated_ten_pull_count, "characters" : user_data["characters"]}}
            else:
                updated_post = {"$set": {"ten_pulls": updated_ten_pull_count}}
            await pompomDB.update_one(filter, updated_post)

            with ThreadPoolExecutor() as executor:
                future = executor.submit(self.img_process, results)
                file = future.result()

            if [result for result in results if result in self.five_stars] != []:
                embed_color = 0xedcb01 # 5 star pull embed color
            else:
                embed_color = 0xa000c8 # 4 star pull embed color

            pulls_embed = discord.Embed(title="Warp Simulator", color=embed_color)
            if [result for result in results if result in self.five_stars] != []:
                pulls_embed.set_image(url="https://cdn.discordapp.com/attachments/1117016812069081140/1117017484000772096/five_star.gif")
            else:
                pulls_embed.set_image(url="https://cdn.discordapp.com/attachments/1117016812069081140/1117017472940384317/four_star.gif")
            pulls_embed.set_footer(text="Good news! You can now view the characters you pull by typing `/my_characters`")

            msg = await ctx.send(embed=pulls_embed)

            pulls_embed.add_field(name="4 Stars:", value=", ".join(set([result for result in results if result in self.four_stars])), inline=False)
            if [result for result in results if result in self.five_stars] != []:
                pulls_embed.add_field(name="5 Stars:", value=", ".join(set([result for result in results if result in self.five_stars])), inline=False)
            else:
                pulls_embed.add_field(name="5 Stars:", value="--", inline=False)
            pulls_embed.set_image(url="attachment://pulls.png")

            await asyncio.sleep(12)
            await msg.edit(attachments=[file], embed=pulls_embed)

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
            # five_star_prob = 0.006 -> 0.001
            five_star_prob = 0.0001
            four_star_prob = four_star_probabilities[self.fourstarPity]
            three_star_prob = 1 - (four_star_prob + five_star_prob)
            probability = {
                3 : three_star_prob/len(self.three_stars),
                4 : four_star_prob/len(self.four_stars),
                5 : five_star_prob/len(self.five_stars)
            }
        return probability

    @warp.error
    async def cooldown_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            seconds_remaining = int(error.retry_after)
            await interaction.response.send_message(f"You can warp again after `{seconds_remaining}` seconds :)", ephemeral=True)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(pom5(client))
