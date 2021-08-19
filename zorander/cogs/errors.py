import logging
import math
import re
import sys
import traceback

import discord
from cachetools import TTLCache
from discord import Color, Embed, Member
from discord.channel import VoiceChannel
from discord.ext import commands
from discord.ext.commands import Cog, command
from discord.utils import get
from typing import TYPE_CHECKING

from zorander import Bot

class MessageNotFound(commands.CommandError):
    def __str__(self):
        return "Reply to a command to re-run it!"


class Errors(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error) -> None:
        if hasattr(ctx.command, "on_error"):
            return

        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.BotMissingPermissions):
            missing = [
                perm.replace("_", " ").replace("guild", "server").title()
                for perm in error.missing_perms
            ]
            if len(missing) > 2:
                fmt = "{}, and {}".format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = " and ".join(missing)
            _message = f"I need the **{fmt}** permission(s) to run this command."
            embed = Embed(
                title="I am Missing Permissions",
                color=Color.red(),
                description=_message,
            )
            await ctx.reply(embed=embed)

        if isinstance(error, commands.DisabledCommand):
            embed = Embed(
                title="Disabled Command",
                color=Color.red(),
                description="This command has been disabled.",
            )
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.CommandOnCooldown):
            embed = Embed(
                title="Command on Cooldown",
                color=Color.red(),
                description=f"TThis command is on cooldown, please retry in {math.ceil(error.retry_after)}s.",
            )
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.MissingPermissions):
            missing = [
                perm.replace("_", " ").replace("guild", "server").title()
                for perm in error.missing_perms
            ]
            if len(missing) > 2:
                fmt = "{}, and {}".format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = " and ".join(missing)
            _message = "You need the **{}** permission(s) to use this command.".format(
                fmt
            )
            embed = Embed(
                title="You are Missing Permissions",
                color=Color.red(),
                description=_message,
            )
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.MissingRequiredArgument):
            e = await self.bot.help_command.send_help(ctx.command)
            e.set_footer(text=f"Invoked by {ctx.author} | Missing Required Arguments")
            await ctx.send(embed=e)

            return

        if isinstance(error, commands.NoPrivateMessage):
            try:
                embed = Embed(
                    title="Guild Only Command",
                    color=Color.red(),
                    description="This command cannot be used in direct messages.",
                )
                await ctx.author.send(embed=embed)
            except discord.Forbidden:
                pass
            return

        else:
            title = " ".join(
                re.compile(r"[A-Z][a-z]*").findall(error.__class__.__name__)
            )
            await ctx.reply(
                embed=discord.Embed(
                    title=title, description=str(error), color=Color.red()
                )
            )
            raise error


def setup(bot: Bot) -> None:
    bot.add_cog(Errors(bot))
