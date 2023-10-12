import discord
from discord.ext import commands
import json
from hsr_timer.HSRtimer import HsrTimersSheet

class StarRailTimers(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        try:
            with open('hsr_timer/hsr_timers.json', 'r') as timers_file:
                self.timers_data = json.load(timers_file)
        except FileNotFoundError:
            pass

    @commands.hybrid_command(name="update_timers", with_app_command=False, hidden=True)
    async def update_timers(self, ctx: commands.Context):
        if ctx.author.id == 376007403398758400 or ctx.author.id == 248347746187083777:
            await ctx.defer()
            try:
                timers_sheet = HsrTimersSheet()
                banner = timers_sheet.get_banner()
                main_data, embed_fields = timers_sheet.sheet_timers_embed()
                data = {
                    'title': main_data[0],
                    'description': main_data[1],
                    'color': main_data[2],
                    'banner': banner,
                    'fields': embed_fields
                }
                with open('hsr_timer/hsr_timers.json', 'w', encoding='utf-8') as timers_file:
                    json.dump(data, timers_file, indent=4)

                await ctx.send("<a:check:1129029037214400652> `/timers` was successfully updated!")

                self.timers_data = data

            except Exception as e:
                await ctx.send(f"Timers update failed :( The following error occured: \n`{e}`")
        else:
            pass

    @commands.hybrid_command(name="timers", description="Get the duration of certain events, banners, etc.")
    async def timers(self, ctx: commands.Context):
        title, description, color, banner = self.timers_data['title'], self.timers_data['description'], int(self.timers_data['color'], 16), self.timers_data['banner']
        fields = self.timers_data['fields']

        banner_embed = discord.Embed(color=color).set_image(url=banner)

        if not description == "-":
            timers_embed = discord.Embed(title=title, description=description, color=color)
        else:
            timers_embed = discord.Embed(title=title, color=color)
        for field in fields:
            try:
                timers_embed.add_field(name=field[0], value=field[1], inline=False)
            except IndexError:
                print("Timers command couldn't find a name or value for the embed")
                continue

        timers_embed.set_footer(text="Credits to @littlemari for making the timers & banner!")

        await ctx.send(embeds=(banner_embed, timers_embed))


async def setup(client: commands.Bot) -> None:
    await client.add_cog(StarRailTimers(client))
