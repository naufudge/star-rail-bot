import discord
from discord import app_commands
from discord.ext import commands
from io import BytesIO
import time
import asyncio
import numpy as np
from pymongo.collection import Collection
from concurrent.futures import ThreadPoolExecutor
from helpers.pom_funcs import find_from_db, find_user_cooldowns, standard_warps
from warps.warp import ten_pull
from warps.data.banners import seele_banner, jing_yuan_banner, kafka_banner, luocha_banner, silver_wolf_banner, blade_banner, imbibitor_lunae_banner
from warps.probabilities import *


class pom5(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.four_star_Pity, self.fivestarPity = 1, 1

    @commands.hybrid_command(name="warp", description="Try out your luck in this Warp Simulator!")
    @app_commands.describe(warp_name="Choose one of the available Warps")
    @app_commands.choices(warp_name=[
        app_commands.Choice(name="Stellar Warp", value=1),
        app_commands.Choice(name="Seele Banner", value=2),
        app_commands.Choice(name="Jing Yuan Banner", value=3),
        app_commands.Choice(name="Silver Wolf Banner", value=4),
        app_commands.Choice(name="Luocha Banner", value=5),
        app_commands.Choice(name="Kafka Banner", value=6),
        app_commands.Choice(name="Blade Banner", value=7),
        app_commands.Choice(name="Imbibitor Lunae Banner", value=8),
    ])
    async def warp(self, ctx: commands.Context, *, warp_name: app_commands.Choice[int]):
        if warp_name.name.lower() == "":
            return

        await ctx.defer()
        pompomDB: Collection = self.client.user_data_collection
        cooldownsDB: Collection = self.client.user_cooldowns
        user_data = await find_from_db(pompomDB, ctx.author.id)
        user_cooldowns = await find_user_cooldowns(cooldownsDB, ctx.author.id)

        if ((int(time.time() - user_cooldowns['last_warp_time'])) < 3600) and user_cooldowns['available_warps'] == 0:
            cooldown_embed = discord.Embed(
                title="You're on cooldown",
                description=f"Please wait `{int((3600 - (time.time() - user_cooldowns['last_warp_time']))/60)}` minutes to warp again :)",
                color=0xffffff
                )
            await ctx.send(embed=cooldown_embed, ephemeral=True)
            return
        elif ((int(time.time() - user_cooldowns['last_warp_time'])) < 3600) and not user_cooldowns['available_warps'] == 0:
            available_warps = user_cooldowns['available_warps']
        elif ((int(time.time() - user_cooldowns['last_warp_time'])) > 3600) and user_cooldowns['available_warps'] <= 10:
            available_warps = 10

        # Standard Banner
        if warp_name.value == 1 or warp_name.name.lower() == "stellar warp":
            banner = standard_warps

        elif warp_name.value == 2 or warp_name.name.lower() in ["seele banner", "seele"]:
            banner = seele_banner

        elif warp_name.value == 3 or warp_name.name.lower() in ["jing yuan banner", "jing yuan"]:
            banner = jing_yuan_banner

        elif warp_name.value == 4 or warp_name.name.lower() in ["silver wolf banner", "silver wolf"]:
            banner = silver_wolf_banner

        elif warp_name.value == 5 or warp_name.name.lower() in ["luocha banner", "luocha"]:
            banner = luocha_banner

        elif warp_name.value == 6 or warp_name.name.lower() in ["kafka banner", "kafka"]:
            banner = kafka_banner

        elif warp_name.value == 7 or warp_name.name.lower() in ["blade banner", "blade"]:
            banner = blade_banner

        elif warp_name.value == 8 or warp_name.name.lower() in ["imbibitor lunae banner", "il", "imbibitor lunae"]:
            banner = imbibitor_lunae_banner

        three_stars = [chara for chara, deets in banner.items() if deets['rarity'] == 3]
        four_stars = [chara for chara, deets in banner.items() if deets['rarity'] == 4]
        five_stars = [chara for chara, deets in banner.items() if deets['rarity'] == 5]
        five_and_four_stars = [chara for chara, deets in banner.items() if (deets['rarity'] == 5 or deets['rarity'] == 4) and (deets['type'] == 'character')]

        chara_names = list(banner)
        rarities = [banner[chara]['rarity'] for chara in chara_names]

        self.five_star_Pity = user_data['five_star_pity']

        results = [] # This will contain the characters/weapons that a user gets from the 10 pull
        for pull in range(1, 11):
            probability = self.probability_calculator(three_stars, four_stars, five_stars)
            chances = [probability[rarity] for rarity in rarities]

            self.four_star_Pity += 1
            chara = np.random.choice(chara_names, p=chances)
            results.append(chara)
            if chara in four_stars:
                self.four_star_Pity = 1
            if chara in five_stars:
                self.five_star_Pity = 1

        # List of characters currently owned by the user
        list_of_charas_owned = list(user_data["characters"])
        # List of 4 or 5 star CHARACTERS that the user just got
        list_of_starCharas_got = [result for result in results if result in five_and_four_stars]
        # List of 5 stars that the user just got (if any)
        list_of_5_stars_gotten = [result for result in results if result in five_stars]

        if not list_of_5_stars_gotten:
            self.five_star_Pity += 1

        for chara_got in list_of_starCharas_got:
            if not chara_got in list_of_charas_owned:
                user_data["characters"][chara_got] = 1
                list_of_charas_owned.append(chara_got)
            else:
                user_data["characters"][chara_got] += 1

        updated_ten_pull_count = user_data["ten_pulls"] + 1
        updated_user_exp = user_data['exp'] + np.random.randint(1, 10)

        if list_of_starCharas_got != []:
            updated_post = {"$set": {"ten_pulls": updated_ten_pull_count, "characters": user_data["characters"], "exp": updated_user_exp, "five_star_pity": self.five_star_Pity}}
        else:
            updated_post = {"$set": {"ten_pulls": updated_ten_pull_count, "exp": updated_user_exp, "five_star_pity": self.five_star_Pity}}
        updated_cds = {"$set": {"last_warp_time": int(time.time()), "available_warps": available_warps - 1}}

        with ThreadPoolExecutor() as executor:
            future = executor.submit(self.img_process, results)
            file = future.result()
        # Update the MongoDB collections
        await pompomDB.update_one({'_id': ctx.author.id}, updated_post)
        await cooldownsDB.update_one({'_id': ctx.author.id}, updated_cds)

        pulls_embed = discord.Embed(title=f"Warp Simulator - {warp_name.name}")
        if list_of_5_stars_gotten != []:
            # 5* pull embed color and 5* warp animation
            pulls_embed.color = 0xedcb01
            pulls_embed.set_image(url="https://cdn.discordapp.com/attachments/1117016812069081140/1117017484000772096/five_star.gif")
        else:
            # 4* pull embed color and 4* warp animation
            pulls_embed.color = 0xa000c8
            pulls_embed.set_image(url="https://cdn.discordapp.com/attachments/1117016812069081140/1117017472940384317/four_star.gif")
        pulls_embed.set_footer(text="Check out the brand new /warp banners! If you encounter any errors/problems contact me (@nauf) ASAP!")

        msg = await ctx.send(embed=pulls_embed)

        pulls_embed.add_field(name="4 Stars:", value=", ".join(set([result for result in results if result in four_stars])), inline=False)
        if list_of_5_stars_gotten != []:
            pulls_embed.add_field(name="5 Stars:", value=", ".join(set(list_of_5_stars_gotten)), inline=False)
        else:
            pulls_embed.add_field(name="5 Stars:", value="--", inline=False)
        pulls_embed.set_image(url="attachment://pulls.png")

        await asyncio.sleep(12.5)
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

    def probability_calculator(self, three_stars, four_stars, five_stars):
        if self.five_star_Pity == 90:
            probability = {
                3 : 0,
                4 : 0,
                5 : 1/len(five_stars)
            }
        elif self.four_star_Pity == 10:
            probability = {
                3 : 0,
                4 : 1/len(four_stars),
                5 : 0
            }
        else:
            # five_star_prob = 0.006 -> 0.001 -> 0.0001 -> 0.0015 REMEMBER TO CHANGE BELOW
            five_star_prob = 0.005
            four_star_prob = four_star_probabilities[self.four_star_Pity]
            three_star_prob = 1 - (four_star_prob + five_star_prob)
            probability = {
                3 : three_star_prob/len(three_stars),
                4 : four_star_prob/len(four_stars),
                5 : five_star_prob/len(five_stars)
            }
        return probability

    # @warp.error
    # async def warp_error(self, ctx: commands.Context, error: commands.HybridCommandError):
    #     if isinstance(error.original, app_commands.CommandOnCooldown):
    #         seconds_remaining = int(error.original.retry_after)
    #         await ctx.send(f"You can warp again after `{seconds_remaining}` seconds :)", ephemeral=True)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(pom5(client))
