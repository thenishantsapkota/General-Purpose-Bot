import asyncio
import re
from datetime import datetime, timedelta
from typing import Optional

import discord
from discord import Color, Embed, Guild, Member, Role, User
from discord.ext import commands
from discord.ext.commands import Cog, command
from discord.ext.commands.converter import Greedy
from discord.message import PartialMessage

from zorander import Bot
from zorander.core.models import ModerationRoles, MuteModel, WarnModel
from zorander.utils.permissions import Permissions
from zorander.utils.time import *

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> float:
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k] * float(v)
            except KeyError:
                raise commands.BadArgument(
                    "{} is an invalid time-key! h/m/s/d are valid!".format(k)
                )
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))
        return time


class Mod(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.permissions = Permissions()
        self.time_convertor = TimeConverter

    @command(name="mute", aliases=["silence"])
    async def mute_command(
        self,
        ctx: commands.Context,
        members: Greedy[Member],
        time: Optional[TimeConverter] = 600,
        *,
        reason: Optional[str] = "No reason specified.",
    ) -> None:
        """Mute a member from the server."""
        author = ctx.author
        guild = ctx.guild
        await self.permissions.staff_role_check(ctx, guild)
        muted_role = await self.permissions.muted_role_check(guild)
        log_channel = await self.permissions.log_channel_check(guild)
        unmutes = []
        pretty_time = pretty_timedelta(timedelta(seconds=time))
        for member in members:
            self.permissions.has_higher_role(author, member)
            if muted_role not in member.roles:
                end_time = datetime.now() + timedelta(seconds=time)
                role_ids = ",".join([str(r.id) for r in member.roles])
                model, _ = await MuteModel.get_or_create(
                    guild_id=guild.id,
                    member_id=member.id,
                    time=end_time,
                    role_id=role_ids,
                )
                await model.save()
                if ctx.guild.premium_subscriber_role in member.roles:
                    await member.edit(
                        roles=[muted_role, ctx.guild.premium_subscriber_role],
                        reason="Muted the User",
                    )
                elif ctx.guild.premium_subscriber_role not in member.roles:
                    await member.edit(roles=[muted_role], reason="Muted the user.")

                embed = Embed(
                    description=f"**:mute: Muted {member} [ID {member.id}]\nTime: {pretty_time}**",
                    color=Color.red(),
                    timestamp=datetime.utcnow(),
                )
                embed.set_author(
                    name=f"{author} [ID {author.id}]",
                    icon_url=author.avatar_url,
                )
                embed.add_field(name="Reason", value=reason)
                embed.set_thumbnail(url=member.avatar_url)
                await log_channel.send(embed=embed)
                await ctx.send(f":mute: Muted `{member.name}` for {pretty_time}.")

                if time:
                    unmutes.append(member)
            else:
                await ctx.send("Member is already muted.", delete_after=10)
            try:
                await member.send(
                    f":mute: Muted from {guild.name} for {reason}.\nTime: {pretty_time}"
                )
            except discord.Forbidden:
                pass

        if len(unmutes):
            await asyncio.sleep(time)
            await self.unmute_handler(ctx, members)

    @command(
        name="unmute", aliases=["unsilence"], brief="Unmute a member from the server."
    )
    async def unmute_command(
        self,
        ctx: commands.Context,
        members: Greedy[Member],
        *,
        reason: Optional[str] = "No reason provided.",
    ) -> None:
        """Unmute a member from the server."""
        author = ctx.author
        guild = ctx.guild
        await self.permissions.mod_role_check(ctx, guild)
        await self.unmute_handler(ctx, members, reason=reason)

    async def unmute_handler(
        self, ctx, members, *, reason="Mute Duration Expired!"
    ) -> None:
        muted_role = await self.permissions.muted_role_check(ctx.guild)
        guild = ctx.guild
        author = ctx.author
        log_channel = await self.permissions.log_channel_check(ctx.guild)
        for member in members:
            if muted_role in member.roles:
                model = await MuteModel.get(guild_id=guild.id, member_id=member.id)
                role_ids = model.role_id
                roles = [
                    guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)
                ]
                await model.delete()
                await member.edit(roles=roles, reason="Unmuted the user.")
                embed = Embed(
                    description=f"**:loud_sound: Unmuted {member} [ID {member.id}]**",
                    color=Color.green(),
                    timestamp=datetime.utcnow(),
                )
                embed.set_author(
                    name=f"{author} [ID {author.id}]",
                    icon_url=author.avatar_url,
                )
                embed.add_field(name="Reason", value=reason)
                embed.set_thumbnail(url=member.avatar_url)
                await log_channel.send(embed=embed)
                await ctx.send(f":loud_sound: Unmuted `{member.name}`.")
            else:
                await log_channel.send(
                    "Looks like Member is already unmuted.\nIgnoring this exception."
                )
            try:
                await member.send(f":loud_sound: Unmuted from `{guild.name}`")
            except discord.Forbidden:
                pass

    @command(name="kick", aliases=["boot"])
    async def kick_command(
        self, ctx: commands.Context, members: Greedy[Member], *, reason: str
    ) -> None:
        """Kick the member from the server."""
        author = ctx.author
        guild = ctx.guild
        await self.permissions.mod_role_check(ctx, guild)
        log_channel = await self.permissions.log_channel_check(guild)
        for member in members:
            self.permissions.has_higher_role(author, member)
            await member.kick(reason=reason)
            embed = Embed(
                color=Color.red(),
                timestamp=datetime.utcnow(),
                description=f"**:boot: Kicked {member} [ID {member.id}]**",
            )
            embed.set_author(
                name=f"{author} [ID {author.id}]",
                icon_url=author.avatar_url,
            )
            embed.add_field(name="Reason", value=reason)
            embed.set_thumbnail(url=member.avatar_url)
            await log_channel.send(embed=embed)
            await ctx.send(f":boot: Kicked `{member.name}.`")
            try:
                await member.send(
                    f":boot: You have been kicked from {guild.name} for reason:`{reason}`"
                )
            except discord.Forbidden:
                pass

    @command(name="ban", aliases=["hammer"])
    async def ban_command(
        self, ctx: commands.Context, members: Greedy[Member], reason: str
    ) -> None:
        author = ctx.author
        guild = ctx.guild

        await self.permissions.mod_role_check(ctx, guild)
        log_channel = await self.permissions.log_channel_check(guild)
        for member in members:
            self.permissions.has_higher_role(author, member)
            await guild.ban(member, reason=reason)
            embed = Embed(
                color=Color.red(),
                timestamp=datetime.utcnow(),
                description=f"**:hammer: Banned {member} [ID {member.id}]**",
            )
            embed.set_author(
                name=f"{author} [ID {author.id}]",
                icon_url=author.avatar_url,
            )
            embed.add_field(name="Reason", value=reason)
            embed.set_thumbnail(url=member.avatar_url)
            await log_channel.send(embed=embed)
            await ctx.send(f":hammer: Banned `{member.name}.`")
            try:
                await member.send(
                    f":hammer: You have been banned from `{guild.name}` for reason - `{reason}`."
                )
            except discord.Forbidden:
                pass

    @command(name="unban")
    async def unban_command(self, ctx: commands.Context, user_id: int) -> None:
        author = ctx.author
        guild = ctx.guild
        await self.permissions.mod_role_check(ctx, guild)
        log_channel = await self.permissions.log_channel_check(guild)
        member = await self.bot.fetch_user(user_id)
        await guild.unban(member)
        embed = Embed(
            color=Color.green(),
            timestamp=datetime.utcnow(),
            description=f"**:unlock: Unbanned {member} [ID {member.id}]**",
        )
        embed.set_author(
            name=f"{author} [ID {author.id}]",
            icon_url=author.avatar_url,
        )
        embed.add_field(name="Reason", value="Unbanned by Admin")
        embed.set_thumbnail(url=member.avatar_url)
        await log_channel.send(embed=embed)
        await ctx.send(f":unlock: Unbanned `{member.name}.`")


def setup(bot: Bot) -> None:
    bot.add_cog(Mod(bot))
