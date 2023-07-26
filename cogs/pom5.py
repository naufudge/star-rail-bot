import discord
from discord import app_commands
from discord.ext import commands
from io import BytesIO
import json
import asyncio
import numpy as np
from pymongo.collection import Collection
from concurrent.futures import ThreadPoolExecutor
from helpers.pom_funcs import find_from_db, standard_warps
from warps.warp import ten_pull
from warps.probabilities import *


class pom5(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.three_stars = [chara for chara, deets in standard_warps.items() if deets['rarity'] == 3]
        self.four_stars = [chara for chara, deets in standard_warps.items() if deets['rarity'] == 4]
        self.five_stars = [chara for chara, deets in standard_warps.items() if deets['rarity'] == 5]
        self.fourstarPity, self.fivestarPity = 1, 1

    @commands.hybrid_command(name="warp", description="Try out your luck in this Warp Simulator!")
    @app_commands.describe(warp_name="Choose one of the available Warps")
    @app_commands.choices(warp_name=[
        app_commands.Choice(name="Stellar Warp", value=1)
    ])
    @app_commands.checks.cooldown(rate=10, per=120, key=lambda i: (i.user.id))
    async def warp(self, ctx: commands.Context, *, warp_name: app_commands.Choice[int]):
        # Standard Banner
        if warp_name.value == 1 or warp_name.name.lower() == "stellar warp":
            await ctx.defer()
            # List of 4 & 5 star characters
            self.five_and_four_stars = [chara for chara, deets in standard_warps.items() if (deets['rarity'] == 5 or deets['rarity'] == 4) and (deets['type'] == 'character')]

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

            pompomDB: Collection = self.client.user_data_collection
            user_data = await find_from_db(pompomDB, ctx.author.id)
            # List of characters currently owned by the user
            list_of_charas_owned = list(user_data["characters"])
            # List of 4 or 5 stars that the user just got
            list_of_starCharas_got = [result for result in results if result in self.five_and_four_stars]

            for chara_got in list_of_starCharas_got:
                if not chara_got in list_of_charas_owned:
                    user_data["characters"][chara_got] = 1
                    list_of_charas_owned.append(chara_got)
                else:
                    user_data["characters"][chara_got] += 1

            updated_ten_pull_count = user_data["ten_pulls"] + 1
            updated_user_exp = user_data['exp'] + np.random.randint(1, 10)

            if list_of_starCharas_got != []:
                updated_post = {"$set": {"ten_pulls": updated_ten_pull_count, "characters": user_data["characters"], "exp": updated_user_exp}}
            else:
                updated_post = {"$set": {"ten_pulls": updated_ten_pull_count, "exp": updated_user_exp}}
            await pompomDB.update_one({'_id': ctx.author.id}, updated_post)

            with ThreadPoolExecutor() as executor:
                future = executor.submit(self.img_process, results)
                file = future.result()

            # List of 5 stars that the user just got (if any)
            list_of_5_stars_gotten = [result for result in results if result in self.five_stars]

            pulls_embed = discord.Embed(title="Warp Simulator")
            if list_of_5_stars_gotten != []:
                # 5* pull embed color and 5* warp animation
                pulls_embed.color = 0xedcb01
                pulls_embed.set_image(url="https://cdn.discordapp.com/attachments/1117016812069081140/1117017484000772096/five_star.gif")
            else:
                # 4* pull embed color and 4* warp animation
                pulls_embed.color = 0xa000c8
                pulls_embed.set_image(url="https://cdn.discordapp.com/attachments/1117016812069081140/1117017472940384317/four_star.gif")
            pulls_embed.set_footer(text="Check out the brand new /leaderboards!")

            msg = await ctx.send(embed=pulls_embed)

            pulls_embed.add_field(name="4 Stars:", value=", ".join(set([result for result in results if result in self.four_stars])), inline=False)
            if list_of_5_stars_gotten != []:
                pulls_embed.add_field(name="5 Stars:", value=", ".join(set(list_of_5_stars_gotten)), inline=False)
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
        if self.fourstarPity == 10:
            probability = {
                3 : 0,
                4 : 1/len(self.four_stars),
                5 : 0
            }
        else:
            # five_star_prob = 0.006 -> 0.001 -> 0.0001
            five_star_prob = 0.001
            four_star_prob = four_star_probabilities[self.fourstarPity]
            three_star_prob = 1 - (four_star_prob + five_star_prob)
            probability = {
                3 : three_star_prob/len(self.three_stars),
                4 : four_star_prob/len(self.four_stars),
                5 : five_star_prob/len(self.five_stars)
            }
        return probability

    @warp.error
    async def warp_error(self, ctx: commands.Context, error: commands.HybridCommandError):
        if isinstance(error.original, app_commands.CommandOnCooldown):
            seconds_remaining = int(error.original.retry_after)
            await ctx.send(f"You can warp again after `{seconds_remaining}` seconds :)", ephemeral=True)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(pom5(client))
