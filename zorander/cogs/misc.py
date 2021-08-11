import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import discord
from cachetools import TTLCache
from discord import Embed, Member
from discord.channel import VoiceChannel
from discord.ext import commands
from discord.ext.commands import Cog, command
from snowflakeapi import SnowClient

from zorander import Bot

from ..utils.time import pretty_datetime, pretty_seconds, pretty_timedelta


class Misc(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.client = SnowClient(os.environ.get("SNOWFLAKE_API_KEY"))

    @command()
    async def ping(self, ctx):
        """Check the response time of the bot."""
        embed = Embed(title="Pinging the API....")
        msg = await ctx.send(embed=embed)
        ping_embed = Embed(
            title="Ping",
            description=f"Response: {pretty_timedelta(msg.created_at - ctx.message.created_at)}\nGateway: {pretty_timedelta(timedelta(seconds=self.bot.latency))}",
        )
        await msg.edit(embed=ping_embed)

    @command(name="whois")
    @commands.guild_only()
    async def whois_command(
        self, ctx: commands.Context, member: Optional[Member]
    ) -> None:
        """See description about a user."""
        author = ctx.author
        guild = ctx.guild
        member = member or author

        embed = Embed(description="", color=self.bot.color)

        if member.bot:
            embed.description = "Looks like you are viewing a bot.\n\n"

        embed.description += f"**Info of** {member.mention}"
        embed.add_field(name="Status", value=str(member.status).title())

        if member.activity:
            activities = []
            for activity in member.activities:
                activities.append(activity.name)
        activity_list = "\n".join(
            [f"{i+1}. {activity_name}" for (i, activity_name) in enumerate(activities)]
        )
        embed.add_field(name="Activity", value=activity_list)

        now = datetime.now()
        created_at = member.created_at
        joined_at = member.joined_at

        embed.add_field(
            name="Account Created on ",
            value=f"{pretty_datetime(created_at)} • {pretty_timedelta(now-created_at)} ago",
            inline=False,
        )
        embed.add_field(
            name="Joined the server on",
            value=f"{pretty_datetime(joined_at)} • {pretty_timedelta(now - joined_at)} ago",
        )
        if len(member.roles) > 1:
            embed.add_field(
                name="Roles",
                value=" ".join(role.mention for role in reversed(member.roles[1:])),
                inline=False,
            )
        embed.set_footer(text=f"ID:{str(member.id)} • Requested by {author}")

        embed.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=embed)

    @command(name="serverinfo")
    @commands.guild_only()
    async def serverinfo_command(self, ctx: commands.Context) -> None:
        """Show information about the server."""
        guild = ctx.guild

        desc = dict(ID=guild.id)

        embed = Embed(
            title=guild.name,
            description="\n".join(
                "**{}**: {}".format(key, value) for key, value in desc.items()
            ),
            timestamp=guild.created_at,
            color=self.bot.color,
        )
        embed.add_field(
            name="Owner",
            value=guild.owner.mention,
        )
        embed.add_field(name="Region", value=str(guild.region).title())
        channels = {discord.TextChannel: 0, discord.VoiceChannel: 0}

        for channel in guild.channels:
            for channel_type in channels:
                if isinstance(channel, channel_type):
                    channels[channel_type] += 1

        channels_desc = "{} {}\n{} {}".format(
            "<:text_channel:872814844280184842>",
            channels[discord.TextChannel],
            "<:voice_channel:872814955349557358>",
            channels[discord.VoiceChannel],
        )

        embed.add_field(name="Channels", value=channels_desc)

        if guild.features:
            embed.add_field(
                name="Features",
                value="\n".join(
                    "• " + feature.replace("_", " ").title()
                    for feature in guild.features
                ),
            )

        statuses = dict(online=0, idle=0, dnd=0, offline=0)

        total_online = 0

        for member in guild.members:
            status_str = str(member.status)
            if status_str != "offline":
                total_online += 1
            statuses[status_str] += 1

        member_desc = "{} {} {} {} {} {} {} {}".format(
            "<:online:872814500087218216>",
            statuses["online"],
            "<:idle:872814573307170837>",
            statuses["idle"],
            "<:dnd:872814628219019284>",
            statuses["dnd"],
            "<:offline:872814689187426364>",
            statuses["offline"],
        )

        embed.add_field(
            name="Members ({}/{})".format(total_online, len(guild.members)),
            value=member_desc,
            inline=False,
        )
        boost_desc = "Level {} - {} Boosts".format(
            guild.premium_tier, guild.premium_subscription_count
        )

        if guild.premium_subscribers:
            booster = sorted(guild.premium_subscribers, key=lambda m: m.premium_since)[
                -1
            ]
            boost_desc += "\nLast boost by {} {} ago".format(
                booster.mention,
                pretty_timedelta(datetime.utcnow() - booster.premium_since),
            )
        # ignore all other exception types, but print them to stderr
        embed.add_field(name="Server Boost", value=boost_desc)

        embed.set_thumbnail(url=guild.icon_url)
        embed.set_footer(text=f"Requested by {ctx.author}")

        await ctx.send(embed=embed)

    @command(name="pypi")
    @commands.guild_only()
    async def pypi_command(self, ctx: commands.Context, module_name: str) -> None:
        data = await self.client.pypi(module_name)
        module = data["module"]
        module_name = module["name"]
        module_description = module["description"]
        module_url = module["url"]
        module_version = module["version"]
        module_author = module["author"]
        registry = data["registry"]

        embed = Embed(
            color=self.bot.color,
            timestamp=datetime.utcnow(),
            description=f"**Module Name** - {module_name}\n**Description** - {module_description}\n**URL** - {module_url}\n**Version** - {module_version}\n**Author** - {module_author}",
        )
        embed.set_thumbnail(url=str(data["icon"]))
        embed.set_footer(text=f"Requested by {ctx.author}")
        embed.set_author(name=f"Info of {module_name} - {registry}")
        await ctx.send(embed=embed)

    @command(name="npm")
    @commands.guild_only()
    async def npm_command(self, ctx: commands.Context, module_name: str) -> None:
        data = await self.client.npm(module_name)
        registry = data["registry"]
        icon = data["icon"]
        module = data["module"]
        module_description = module["description"]
        module_name = module["name"]
        module_version = module["version"]
        module_author = module["author"]
        module_url = module["url"]

        embed = Embed(
            color=self.bot.color,
            timestamp=datetime.utcnow(),
            description=f"**Module Name** - {module_name}\n**Description** - {module_description}\n**URL** - {module_url}\n**Version** - {module_version}\n**Author** - {module_author}",
        )
        embed.set_thumbnail(url=str(icon))
        embed.set_footer(text=f"Requested by {ctx.author}")
        embed.set_author(name=f"Info of {module_name} - {registry}")
        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Misc(bot))
