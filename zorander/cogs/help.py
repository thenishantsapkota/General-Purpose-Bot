import asyncio
import os
from pathlib import Path

import discord
from discord import Color, Embed
from discord.ext import commands
from discord.ext.commands import Cog, command
from dotenv import load_dotenv

from zorander import Bot

from ..core.models import GuildModel
from ..utils.utilities import send_embed

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


VERSION = os.getenv("VERSION")
EMOJI = "<:pansweat:858239084363644938>"


class Help(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.bot.remove_command("help")

    @command()
    async def help(self, ctx, *params):
        model = await GuildModel.get_or_none(guild_id=ctx.guild.id)
        prefix = model.prefix
        if not params:
            try:
                owner = ctx.guild.get_member(os.getenv("OWNER_ID")).mention

            except AttributeError:
                owner = os.getenv("OWNER_NAME")
            embed = discord.Embed(
                title="Commands and Cogs",
                color=self.bot.color,
                description=f"Use `{prefix}help <cog>` to gain more information about that Cog.",
            )

            cogs_desc = ""
            for cog in self.bot.cogs:
                if cog == "Help":
                    continue
                cogs_desc += f"`{cog}` {self.bot.cogs[cog].__doc__}\n"

            embed.add_field(name="Cogs", value=cogs_desc, inline=False)

            commands_desc = ""
            for command in self.bot.walk_commands():
                if not command.cog_name and not command.hidden:
                    commands_desc += f"{command.name} - {command.help}\n"

            if commands_desc:
                embed.add_field(
                    name="Not belonging to a Cog.", value=commands_desc, inline=False
                )

                embed.add_field(
                    name="About", value=f"This bot is maintained by {owner}"
                )
                embed.set_footer(text=f"Bot is running Version: {VERSION}")
        elif len(params) == 1:

            for cog in self.bot.cogs:
                if cog.lower() == params[0].lower():

                    embed = discord.Embed(
                        title=f"{cog} - commands",
                        description=self.bot.cogs[cog].__doc__,
                        color=self.bot.color,
                    )

                    for command in self.bot.get_cog(cog).get_commands():
                        if not command.hidden:
                            embed.add_field(
                                name=f"{prefix}{command.name}",
                                value=command.help,
                                inline=False,
                            )
                    break

            else:
                embed = discord.Embed(
                    title=f"Uh Oh?! {EMOJI}",
                    description=f"I've never heard of a cog called `{params[0]}` before.",
                    color=Color.orange(),
                )

        elif len(params) > 1:
            embed = discord.Embed(
                title=f"Uhhhh {EMOJI}",
                description=f"Looks like you passed me more arguments than I actually needed.",
                color=Color.orange(),
            )

        else:
            pass

        await send_embed(ctx, embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Help(bot))
