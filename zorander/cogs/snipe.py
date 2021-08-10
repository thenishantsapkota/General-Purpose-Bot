import asyncio
import logging
import re
from datetime import datetime

import discord
import editdistance
from cachetools import TTLCache
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Cog, command

from zorander import Bot


class Snipe(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.delete_snipes = TTLCache(100, 600)
        self.edit_snipes = TTLCache(100, 600)

    @Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        self.delete_snipes[message.channel] = message

    @Cog.listener()
    async def on_message_edit(
        self, before: discord.Message, after: discord.Message
    ) -> None:
        if before.author.bot:
            return

        self.edit_snipes[after.channel] = (before, after)

    @commands.group(name="snipe", invoke_without_subcommand=False)
    async def snipe_group(self, ctx: commands.Context) -> None:
        """Retrieve the recently deleted message from the channel. Use `edited` keyword to snipe edited messages."""
        try:
            sniped_message = self.delete_snipes[ctx.channel]

        except KeyError:
            await ctx.send(
                "You need to have a deleted message to snipe ya fool.", delete_after=10
            )

        else:
            embed = Embed(
                color=self.bot.color,
                description=f"Deleted Message - {sniped_message.content}",
                timestamp=sniped_message.created_at,
            )
            embed.set_author(
                name=f"Deleted Message from - {sniped_message.author.name}",
                icon_url=sniped_message.author.avatar_url,
            )
            embed.set_footer(text=f"Sniped by {ctx.author} | in #{ctx.channel.name}")
            await ctx.send(embed=embed)

    @snipe_group.command(name="edited")
    async def snipe_edited(self, ctx: commands.Context) -> None:
        try:
            before, after = self.edit_snipes[ctx.channel]
        except KeyError:
            await ctx.send(
                "You need to have a deleted message to snipe ya fool.", delete_after=10
            )
        else:
            embed = Embed(color=self.bot.color, timestamp=after.edited_at)
            embed.add_field(name="Before", value=before.content, inline=False)
            embed.add_field(name="After", value=after.content, inline=False)
            embed.set_author(
                name=f"Edited Message from - {after.author.display_name}",
                icon_url=after.author.avatar_url,
            )
            embed.set_footer(text=f"Sniped by {ctx.author} | in #{ctx.channel.name}")
            await ctx.reply(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Snipe(bot))
