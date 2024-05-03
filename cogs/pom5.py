import discord
from discord import app_commands
from discord.ext import commands
from io import BytesIO
from copy import deepcopy
import time
import asyncio
import numpy as np
from pymongo.collection import Collection
from concurrent.futures import ThreadPoolExecutor
from helpers.pom_funcs import find_from_db, find_user_cooldowns, standard_warps
from warps.warp import ten_pull
from warps.data.banners import *
from warps.probabilities import four_star_probabilities


class pom5(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.four_star_Pity, self.fivestarPity = 1, 1
        self.cooldown = 900 # This is the cooldown between 10 warps in seconds
        self.announcement = False

    @commands.hybrid_command(name="warp", description="Try out your luck in this Warp Simulator!")
    @app_commands.describe(banner_name="Choose one of the available Warps")
    @app_commands.choices(banner_name=[
        app_commands.Choice(name="Stellar Warp", value=1),
        app_commands.Choice(name="Seele", value=2),
        app_commands.Choice(name="Jing Yuan", value=3),
        app_commands.Choice(name="Silver Wolf", value=4),
        app_commands.Choice(name="Luocha", value=5),
        app_commands.Choice(name="Kafka", value=6),
        app_commands.Choice(name="Blade", value=7),
        app_commands.Choice(name="Imbibitor Lunae", value=8),
        app_commands.Choice(name="Fu Xuan", value=9),
        app_commands.Choice(name="Jingliu", value=10),
        app_commands.Choice(name="Topaz & Numby", value=11),
        app_commands.Choice(name="Huohuo", value=12),
        app_commands.Choice(name="Argenti", value=13),
        app_commands.Choice(name="Ruan Mei", value=14),
        app_commands.Choice(name="Dr. Ratio", value=15),
        app_commands.Choice(name="Black Swan", value=16),
        app_commands.Choice(name="Sparkle", value=17),
        app_commands.Choice(name="Acheron", value=18),
        app_commands.Choice(name="Aventurine", value=19),
    ])
    async def warp(self, ctx: commands.Context, *, banner_name: app_commands.Choice[int]):
        if banner_name.name.lower() == "":
            return

        await ctx.defer()
        pompomDB: Collection = self.client.user_data_collection
        cooldownsDB: Collection = self.client.user_cooldowns
        user_data = await find_from_db(pompomDB, ctx.author.id)
        user_cooldowns = await find_user_cooldowns(cooldownsDB, ctx.author.id)
        user_pity: bool = user_cooldowns['pity']

        self.five_star_Pity = user_data['five_star_pity']

        if ((int(time.time() - user_cooldowns['last_warp_time'])) < self.cooldown) and user_cooldowns['available_warps'] == 0:
            cooldown_embed = discord.Embed(
                title="You're on cooldown",
                description=f"Please wait `{int((self.cooldown - (time.time() - user_cooldowns['last_warp_time']))/60)}` minutes to warp again :)",
                color=0xffffff
            ).set_footer(text="50/50 has been added due to high demand! If you get a normal 5 star, your next 5 star will be a limited character.")
            await ctx.send(embed=cooldown_embed, ephemeral=True)
            return
        elif ((int(time.time() - user_cooldowns['last_warp_time'])) < self.cooldown) and not user_cooldowns['available_warps'] == 0:
            available_warps = user_cooldowns['available_warps']
        elif ((int(time.time() - user_cooldowns['last_warp_time'])) > self.cooldown) and user_cooldowns['available_warps'] <= 10:
            available_warps = 10

        # Standard Banner & Other available banners
        banner = deepcopy(base_limited_warp)
        limited_character = None
        match banner_name.value:
            case 1:
                banner = deepcopy(standard_warps)
            case 2:
                limited_character = seele
            case 3:
                limited_character = jing_yuan
            case 4:
                limited_character = silver_wolf
            case 5:
                limited_character = luocha
            case 6:
                limited_character = kafka
            case 7:
                limited_character = blade
            case 8:
                limited_character = imbibitor_lunae
            case 9:
                limited_character = fu_xuan
            case 10:
                limited_character = jingliu
            case 11:
                limited_character = topaz_and_numby
            case 12:
                limited_character = huohuo
            case 13:
                limited_character = argenti
            case 14:
                limited_character = ruan_mei
            case 15:
                limited_character = dr_ratio
            case 16:
                limited_character = black_swan
            case 17:
                limited_character = sparkle
            case 18:
                limited_character = acheron
            case 19:
                limited_character = aventurine
            case _:
                return
            
        if limited_character:
            banner.update(limited_character)

        three_stars = [chara for chara, deets in banner.items() if deets['rarity'] == 3]
        four_stars = [chara for chara, deets in banner.items() if deets['rarity'] == 4]
        five_stars = [chara for chara, deets in banner.items() if deets['rarity'] == 5]
        five_and_four_stars = [chara for chara, deets in banner.items() if (deets['rarity'] == 5 or deets['rarity'] == 4) and (deets['type'] == 'character')]

        # All the names of the characters in the banner as a list
        chara_names = list(banner)
        limited_character_name = list(limited_character.keys())[0]
        rarities = [banner[chara]['rarity'] for chara in chara_names]

        results = [] # This will contain the characters/weapons that a user gets from the 10 pull
        for pull in range(1, 11):
            probability = self.probability_calculator(three_stars, four_stars, five_stars)
            chances = [probability[rarity] for rarity in rarities]
            chara: str = np.random.choice(chara_names, p=chances)
            
            self.four_star_Pity += 1

            if chara in four_stars:
                self.four_star_Pity = 1

            if chara in five_stars:
                if user_pity == True or chara == limited_character_name:
                    chara = limited_character_name
                    user_pity = False
                elif chara != limited_character_name:
                    user_pity = True

            results.append(chara)
            
        # List of characters currently owned by the user
        list_of_charas_owned = list(user_data["characters"])
        # List of 4 or 5 star CHARACTERS that the user just got
        list_of_starCharas_got = [result for result in results if result in five_and_four_stars]
        # List of 5 stars that the user just got (if any)
        list_of_5_stars_gotten = [result for result in results if result in five_stars]

        for chara_got in list_of_starCharas_got:
            if not chara_got in list_of_charas_owned:
                user_data["characters"][chara_got] = 1
                list_of_charas_owned.append(chara_got)
            else:
                user_data["characters"][chara_got] += 1

        # Update user ten pull count
        updated_ten_pull_count = user_data["ten_pulls"] + 1
        # Update the user's total experience by giving them some experience points
        updated_user_exp = user_data['exp'] + np.random.randint(1, 10)

        with ThreadPoolExecutor() as executor:
            future = executor.submit(self.img_process, results)
            file = future.result()
            
        # Update the MongoDB collections
        if list_of_starCharas_got != []:
            updated_post = {"$set": {"ten_pulls": updated_ten_pull_count, "characters": user_data["characters"], "exp": updated_user_exp, "five_star_pity": self.five_star_Pity}}
        else:
            updated_post = {"$set": {"ten_pulls": updated_ten_pull_count, "exp": updated_user_exp, "five_star_pity": self.five_star_Pity}}

        await pompomDB.update_one({'_id': ctx.author.id}, updated_post)

        # footer_texts = [
        #     "Now you can provide feedback, suggestions, or anything in general that you would like to tell me using /feedback.",
        # ]
        pulls_embed = discord.Embed(title=f"Warp Simulator - {banner_name.name}")
        if list_of_5_stars_gotten != []:
            # 5* pull embed color and 5* warp animation
            pulls_embed.color = 0xedcb01
            pulls_embed.set_image(url="https://cdn.discordapp.com/attachments/1117016812069081140/1117017484000772096/five_star.gif")
        else:
            # 4* pull embed color and 4* warp animation
            pulls_embed.color = 0xa000c8
            pulls_embed.set_image(url="https://cdn.discordapp.com/attachments/1117016812069081140/1117017472940384317/four_star.gif")
        pulls_embed.set_footer(text="Now you can provide feedback, suggestions, or anything in general that you would like to tell me using /feedback.")

        msg = await ctx.send(embed=pulls_embed)

        # Show an announcement if you wanna
        if self.announcement and user_cooldowns['message']:
            announcement_embed = discord.Embed(
                title="Announcement!",
                description="Looking for some help with building a support server for Pom-Pom! Only condition is being able to communicate in **English**. \n",
                color=0xf94449
            ).set_footer(text="Add me (@nauf) if you're interested :)")
            await ctx.interaction.followup.send(embed=announcement_embed, ephemeral=True)

            updated_cds = {"$set": {"last_warp_time": int(time.time()), "available_warps": available_warps - 1, "pity": user_pity, "message": False}}
        else:
            updated_cds = {"$set": {"last_warp_time": int(time.time()), "available_warps": available_warps - 1, "pity": user_pity}}

        # Update the cooldowns collection
        await cooldownsDB.update_one({'_id': ctx.author.id}, updated_cds)

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
        # if self.five_star_Pity == 90:
        #     probability = {
        #         3 : 0,
        #         4 : 0,
        #         5 : 1/len(five_stars)
        #     }
        if self.four_star_Pity == 10:
            probability = {
                3 : 0,
                4 : 1/len(four_stars),
                5 : 0
            }
        else:
            # five_star_prob = 0.006 -> 0.001 -> 0.0001 -> 0.0015 REMEMBER TO CHANGE BELOW
            five_star_prob = 0.015
            # five_star_prob = 0.09
            four_star_prob = four_star_probabilities[self.four_star_Pity]
            three_star_prob = 1 - (four_star_prob + five_star_prob)
            probability = {
                3 : three_star_prob/len(three_stars),
                4 : four_star_prob/len(four_stars),
                5 : five_star_prob/len(five_stars)
            }
        return probability


async def setup(client: commands.Bot) -> None:
    await client.add_cog(pom5(client))
