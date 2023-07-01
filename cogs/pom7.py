import discord
from discord.ext import commands
from hsr_timer.hsr_timer import timers

class pom7(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.msgid = 1116670517445939241
        # self.allowed = [] # ccomb, dan heng
        self.allowed = [782971853999702017, 895415743414427740, 1109045025578430504] # ccomb, dan heng, pom-pom-testing

    # SLASH COMMAND VERSION
    # @app_commands.command(name="timers", description="Gives you some dates.")
    # async def hsrTimer(self, interaction: discord.Interaction):
    #     if interaction.guild_id in self.allowed:
    #         titleDesc, fields = timers()

    #         timers_embed = discord.Embed(title=titleDesc[0], description=titleDesc[1], color=0xffffff)
    #         for each in fields:
    #             timers_embed.add_field(name=each[0], value=each[1], inline=False)

    #         await interaction.response.send_message(embed=timers_embed)
    #     else:
    #         await interaction.response.send_message("Sorry :(")

    @commands.command(name="timers", description="Gives you some dates.", hidden=True)
    async def hsrTimer(self, ctx: commands.Context):
        if ctx.guild.id in self.allowed:
            titleDesc, fields = timers()

            timers_embed = discord.Embed(title=titleDesc[0], description=titleDesc[1], color=0xffffff)
            for each in fields:
                timers_embed.add_field(name=each[0], value=each[1], inline=False)

            await ctx.channel.send(embed=timers_embed)
        else:
            await ctx.channel.send("Sorry :(")


    # MESSAGE EDITING TEST
    @commands.command(name="test", description="Message Edit", hidden=True)
    async def editMsg(self, ctx: commands.Context):
        webhook_cog = self.client.get_cog('webhook')
        # await webhook_cog._webhook()

        await ctx.send("did something")
        # await ctx.message.delete()
        # channel = self.client.get_channel(1116655010491662367)
        # msg = await channel.fetch_message(self.msgid)
        # test_embed = discord.Embed(title="Hello World", description="Goodbye world", color=0x000000)
        # await msg.edit(embed=test_embed)

    @editMsg.error
    async def any_error(self, ctx: commands.Context, error):
        print(error)
        await ctx.send("an error occured")

async def setup(client: commands.Bot) -> None:
    await client.add_cog(pom7(client))
