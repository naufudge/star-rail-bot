import discord
from discord.ext import commands
from discord import app_commands
from io import BytesIO
from pymongo.collection import Collection
from warps.inventory_view import inventory_view
from helpers.pom_funcs import level_calculator, exp_required_calculator, find_from_db, all_warp_details

class pom6(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.pompomDB: Collection = client.user_data_collection

    @commands.hybrid_command(name="my_characters", description="View all the characters you got from Warping.")
    async def my_charas(self, ctx: commands.Context):
        await ctx.defer()

        user_data = await find_from_db(self.pompomDB, ctx.author.id)
        user_characters = user_data['characters']

        result = inventory_view(user_characters)

        if not result == None:
            middle_man = BytesIO()
            result.save(middle_man, format="PNG", optimize=True)
            middle_man.seek(0)
            file = discord.File(middle_man, filename="charas.png")

            my_charas_embed = discord.Embed(title=f"{ctx.author.name}'s Characters", color=0xffffff)
            my_charas_embed.set_image(url="attachment://charas.png")

            await ctx.send(file=file, embed=my_charas_embed)
        else:
            my_charas_embed = discord.Embed(title=f"{ctx.author.name}'s Characters", description="You don't have any characters at the moment :( Start collecting by doing `/warp` now!",color=0xffffff)

            await ctx.send(embed=my_charas_embed)

    @commands.hybrid_command(name="profile", description="Check your profile")
    async def profile(self, ctx: commands.Context):
        await ctx.defer()

        user_data = await find_from_db(self.pompomDB, ctx.author.id)

        if not user_data['uid'] == 0:
            uid = user_data['uid']
        else:
            uid = "N/A"
        pulls = user_data['ten_pulls']
        total_4_stars = sum([copies for chara, copies in user_data['characters'].items() if all_warp_details[chara]['rarity'] == 4])
        total_5_stars = sum([copies for chara, copies in user_data['characters'].items() if all_warp_details[chara]['rarity'] == 5])
        current_user_exp = user_data['exp']
        level = level_calculator(current_user_exp)

        profile_embed = discord.Embed(title=f"{ctx.author.name}'s Profile", color=0xffffff)
        profile_embed.set_thumbnail(url=ctx.message.author.avatar)
        profile_embed.add_field(name=f"Level **{int(level)}**:", value=f"`{current_user_exp} / {exp_required_calculator(level + 1)}`")
        profile_embed.add_field(name="Star Rail UID:", value=f"{uid}")
        profile_embed.add_field(name="Warp Command Used:", value=f"{pulls} Times", inline=False)
        profile_embed.add_field(
            name="Total Characters Obtained:",
            value=f"- 4 Stars: *{total_4_stars}* \n- 5 Stars: *{total_5_stars}* \n- Total: *{total_4_stars+total_5_stars}*",
            inline=False
            )

        await ctx.send(embed=profile_embed)

    @commands.hybrid_command(name="set_uid", description="Set/Edit your Star Rail UID and it will be shown on your profile")
    @app_commands.describe(uid="Your Star Rail UID")
    @app_commands.checks.cooldown(rate=1, per=3600, key=lambda i: (i.user.id))
    async def set_edit_uid(self, ctx: commands.Context, uid: int):
        await ctx.defer()
        user_data = await find_from_db(self.pompomDB, ctx.author.id)
        current_uid = user_data['uid']
        if not current_uid == 0:
            self.pompomDB.update_one(user_data, {"$set": {"uid": uid}})
            set_uid_embed = discord.Embed(
                title="Successfully changed UID!",
                description=f"Your UID has been changed to `{uid}`.",
                color=0xffffff
                ).set_footer(text="Set your UID to 0 if you would like to remove it from your profile")
        else:
            self.pompomDB.update_one(user_data, {"$set": {"uid": uid}})
            set_uid_embed = discord.Embed(
                title="UID successfully set!",
                description=f"You have set your UID: `{uid}`.",
                color=0xffffff
            ).set_footer(text="Set your UID to 0 if you would like to remove it from your profile")

        await ctx.send(embed=set_uid_embed, ephemeral=True)

    @set_edit_uid.error
    async def uid_error(self, ctx: commands.Context, error: commands.HybridCommandError):
        if isinstance(error.original, app_commands.CommandOnCooldown):
            minutes_remaining = int(error.original.retry_after/60)
            await ctx.send(f"Sorry, you're on cooldown :( You can change your UID after `{minutes_remaining}` minutes", ephemeral=True)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(pom6(client))
