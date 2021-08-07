import logging
import math
import sys
import traceback

import discord
from cachetools import TTLCache
from discord import Color, Embed, Member
from discord.channel import VoiceChannel
from discord.ext import commands
from discord.ext.commands import Cog, command
from discord.utils import get

from zorander import Bot


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
            # await ctx.reply('This command has been disabled.')
            embed = Embed(
                title="Disabled Command",
                color=Color.red(),
                description="This command has been disabled.",
            )
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.CommandOnCooldown):
            # await ctx.reply("This command is on cooldown, please retry in {}s.".format(math.ceil(error.retry_after)))
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
            # await ctx.reply(_message)
            return

        if isinstance(error, commands.UserInputError):
            await ctx.reply("Invalid input.")
            # await self.reply(ctx)
            return

        if isinstance(error, commands.NoPrivateMessage):
            try:
                embed = Embed(
                    title="Guild Only Command",
                    color=Color.red(),
                    description="This command cannot be used in direct messages.",
                )
                await ctx.author.send(embed=embed)
                # await ctx.author.reply('This command cannot be used in direct messages.')
            except discord.Forbidden:
                pass
            return

        if isinstance(error, commands.CheckFailure):
            await ctx.reply("You do not have permission to use this command.")
            return

        # ignore all other exception types, but print them to stderr
        logging.info("Ignoring exception in command {}:".format(ctx.command))

        traceback.print_exception(type(error), error, error.__traceback__)


def setup(bot: Bot) -> None:
    bot.add_cog(Errors(bot))
