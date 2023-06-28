import discord
import random
from discord.ext import commands
from helpers.pom_views import HelpView


# This is untested and largely coded based on my experience. It would be best to test this out before proceeding :)
# also cogs and commands would need descriptions + appropriate names!
class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={"help": "Show help about the bot, a command, or a category.",})
    
    async def send_bot_help(self, mapping: dict):
        colors = [0xc71e1e, 0xd83131, 0xc97f7f, 0x9a0000, 0x0f0707]
        help_embed = discord.Embed(
            title="__Help__",
            description="Hi Trailblazer! How can Pom-Pom help you today?",
            color=random.choice(colors)
        )
        help_embed.set_footer(text="Made with love by Nauf :)")

        for cog, commands in mapping.items():
            if commands and cog:
                help_embed.add_field(
                    name=f"{cog.qualified_name.upper()}", # This is where naming your cogs comes into play - we can section out your commands in "categories"!
                    value='\n'.join([f"{self.context.clean_prefix}{command.name}\n{command.description}" for command in commands]),
                    # ^ This basically mimics what you had on your old help command but uses 1 field per cog instead of 1 field per command
                    inline=False
                )

        await self.context.send(embed=help_embed, view=HelpView())
    
    async def send_cog_help(self, cog):
        # To be coded
        await self.context.send(cog.description)
    
    async def send_group_help(self, group):
        # To be coded
        await self.context.send(group.qualified_name)
    
    async def send_command_help(self, command: commands.Command):
        # To be coded
        await self.context.send(f"Command: {self.context.clean_prefix}{command.qualified_name}")

async def setup(bot):
    bot.old_help_command = bot.help_command
    bot.help_command = CustomHelpCommand()

async def teardown(bot):
    bot.help_command = bot.old_help_command