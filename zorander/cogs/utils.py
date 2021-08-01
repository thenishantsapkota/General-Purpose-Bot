import asyncio
import logging
from datetime import datetime

import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Cog, command

from zorander import Bot

from ..core.models import GuildModel


class Utils(Cog):
    """Houses utility Commands for the guild."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.bot.sniped_messages = {}

    @command(
        name="changeprefix", aliases=["chp"], brief="Change the prefix of the server."
    )
    async def changeprefix(self, ctx: commands.Context, prefix: str) -> None:
        """Change the prefix of the server."""
        model = await GuildModel.get_or_none(guild_id=ctx.guild.id)
        model.prefix = prefix
        await model.save()
        response = f"The prefix for {ctx.guild} has been changed to `{prefix}.`"
        await ctx.send(response)

    @command(name="hello", brief="Returns the current prefix of the server.")
    async def prefix_command(self, ctx: commands.Context) -> None:
        """Greets the user with the current prefix of the server."""
        model = await GuildModel.get_or_none(guild_id=ctx.guild.id)
        prefix = model.prefix
        response = f"Hello {ctx.author.name}, My prefix here is {self.bot.user.mention} or `{prefix}`\nUse the `{prefix}changeprefix <new_prefix>` command to change it."
        await ctx.send(response)


def setup(bot: Bot) -> None:
    bot.add_cog(Utils(bot))
