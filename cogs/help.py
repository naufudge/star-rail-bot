import discord
import random
from discord.ext import commands
from typing import Optional, Mapping, List
from helpers.pom_views import HelpView


# This is untested and largely coded based on my experience. It would be best to test this out before proceeding :)
# also cogs and commands would need descriptions + appropriate names!
class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        self.colors = [0xc71e1e, 0xd83131, 0xc97f7f, 0x9a0000, 0x0f0707]
        # super().__init__(command_attrs={"help": "Show help about the bot, a command, or a category."})
        super().__init__()

    async def send_bot_help(self, mapping: Mapping[Optional[commands.Cog], List[commands.Command]]):
        colors = [0xc71e1e, 0xd83131, 0xc97f7f, 0x9a0000, 0x0f0707]
        help_embed = discord.Embed(
            title="__Help__",
            description="Hi Trailblazer! How can Pom-Pom help you today?",
            color=random.choice(colors)
        )
        help_embed.set_footer(text="Made with love by Nauf :)")

        for cog, commands in mapping.items():
            if (commands and cog):
                for command in commands:
                    if command.hidden != True and command.clean_params != {}:
                        help_embed.add_field(
                            name = f"`{self.context.clean_prefix}{command.name} <{list(command.clean_params.keys())[0]}>`",
                            value = f"*{command.description}*",
                            inline = False
                        )
                    elif command.hidden != True and command.clean_params == {}:
                        help_embed.add_field(
                            name = f"`{self.context.clean_prefix}{command.name}`",
                            value = f"*{command.description}*",
                            inline = False
                        )

        await self.context.send(embed=help_embed, view=HelpView())

    async def send_cog_help(self, cog):
        # To be coded
        await self.context.send(cog.description)

    async def send_group_help(self, group):
        # To be coded
        await self.context.send(group.qualified_name)

    async def send_command_help(self, command: commands.Command):
        if command.clean_params != {}:
            command_embed = discord.Embed(
                title=f"Command: `{self.context.clean_prefix}{command.qualified_name} <{list(command.clean_params.keys())[0]}>`",
                description=command.description,
                color=random.choice(self.colors)
                )
        else:
            command_embed = discord.Embed(
                title=f"Command: `{self.context.clean_prefix}{command.qualified_name}`",
                description=command.description,
                color=random.choice(self.colors)
                )
        await self.context.send(embed=command_embed)

    async def send_error_message(self, error: str):
        error_embed = discord.Embed(
            title="An Error Occured!",
            description=f"{error} :(",
            color=random.choice(self.colors)
        )
        await self.context.send(embed=error_embed, ephemeral=True)

async def setup(bot):
    bot.old_help_command = bot.help_command
    bot.help_command = CustomHelpCommand()

async def teardown(bot):
    bot.help_command = bot.old_help_command
