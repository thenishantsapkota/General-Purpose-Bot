import re
from typing import Union

import discord
from discord.errors import Forbidden
from discord.ext import commands


async def send_embed(ctx: commands.Context, embed: discord.Embed) -> None:
    try:
        await ctx.send(embed=embed)

    except Forbidden:
        await ctx.author.send(
            f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
            f"May you inform the server team about this issue? :slight_smile:",
            embed=embed,
        )


async def make_embed(
    title: str = "", color=discord.Color.teal(), name="", value="", footer=None
) -> discord.Embed:
    embed = discord.Embed(title=title, color=color)
    embed.add_field(name=name, value=value)
    if footer:
        embed.set_footer(text=footer)

    return embed


