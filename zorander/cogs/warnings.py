from datetime import datetime
from typing import Optional

import discord
from discord import Color, Embed, Member, User
from discord.channel import TextChannel
from discord.ext import commands
from discord.ext.commands import Cog, Greedy, command

from zorander import Bot
from zorander.cogs.mod import Mod
from zorander.core.models import WarningsModel
from zorander.utils.permissions import Permissions
from zorander.utils.time import *


class Warnings(Cog):
    def __init__(self, bot: Bot) -> None:
        """Init Function for the Cog"""
        self.bot = bot
        self.permissions = Permissions()
        self.mod = Mod(bot)

    async def warning_count(self, ctx: commands.Context, member: Member) -> None:
        """Function that checks for amount of warnings"""
        warn_model = await WarningsModel.filter(
            guild_id=ctx.guild.id, member_id=member.id
        )
        if len(warn_model) in range(5, 8):
            await self.mod.mute_handler(
                ctx, [member], 600, f"Warning Count : {len(warn_model)}"
            )
        if len(warn_model) in range(8, 10):
            await self.mod.mute_handler(
                ctx, [member], 21600, f"Warning Count : {len(warn_model)}"
            )
        if len(warn_model) >= 10:
            await self.mod.kick_handler(
                ctx, [member], f"Warning Count : {len(warn_model)}"
            )

    @command(name="warn")
    async def warn_command(
        self, ctx: commands.Context, members: Greedy[Member], *, reason: str
    ) -> None:
        """Warns the members mentioned."""
        author = ctx.author
        guild = ctx.guild
        await self.permissions.staff_role_check(ctx, guild)
        log_channel = await self.permissions.log_channel_check(guild)
        for member in members:
            self.permissions.has_higher_role(author, member)
            model = await WarningsModel.create(
                guild_id=guild.id,
                member_id=member.id,
                reason=reason,
                author_name=author,
                date=pretty_datetime(datetime.now()),
            )
            await model.save()
            embed = Embed(
                color=Color.red(),
                timestamp=datetime.utcnow(),
                description=f"**:warning: Warned {member} [ID {member.id}]**",
            )
            embed.set_author(
                name=f"{author} [ID {author.id}]",
                icon_url=author.avatar_url,
            )
            embed.add_field(name="Reason", value=reason)
            embed.set_thumbnail(url=member.avatar_url)
            await log_channel.send(embed=embed)
            await ctx.send(f":warning: Warned `{member.name}`")
            try:
                await member.send(
                    f":warning: You have been warned in `{guild.name}`\nReason: `{reason}`"
                )

            except discord.Forbidden:
                pass

            await self.warning_count(ctx, member)

    @commands.group(invoke_without_command=True)
    async def warnings(self, ctx: commands.Context, member: Optional[Member]):
        """View the warnings of the member specified."""
        author = ctx.author
        guild = ctx.guild
        await self.permissions.staff_role_check(ctx, guild)
        member = member or author
        warn_model = await WarningsModel.filter(guild_id=guild.id, member_id=member.id)

        warnings = "\n\n".join(
            [
                f"#{model.id} - `{model.date}` - Warned By **{model.author_name}**\n**Reason:**{model.reason}"
                for (i, model) in enumerate(warn_model)
            ]
        )
        embed = Embed(
            color=self.bot.color,
            timestamp=datetime.utcnow(),
            title=f"Warnings-{member}[ID - {member.id}]",
            description=warnings if len(warn_model) else "User hasn't been warned.",
        )
        embed.set_footer(
            text=f"Requested by {author.name} | Total Warnings: {len(warn_model)}"
        )
        await ctx.send(embed=embed)

    @warnings.command(name="delete")
    async def warnings_delete(
        self, ctx: commands.Context, member: Optional[Member], id: int
    ) -> None:
        """Delete individual warnings of a member."""
        author = ctx.author
        guild = ctx.guild
        await self.permissions.mod_role_check(ctx, guild)
        log_channel = await self.permissions.log_channel_check(guild)
        model = await WarningsModel.get_or_none(guild_id=guild.id, id=id)
        await model.delete()
        await ctx.send(f"Deleted Warning #{id} of **{member}**")
        embed = Embed(
            color=Color.green(),
            timestamp=datetime.utcnow(),
            description=f":warning: Deleted Warning #{id} of \n**{member} [ID {member.id}]**",
        )
        embed.set_author(name=f"{author} [ID {author.id}]", icon_url=author.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)
        await log_channel.send(embed=embed)

    @warnings.command(name="clear")
    async def warnings_clear(self, ctx: commands.Context, member: Member) -> None:
        """Clear the warnings of the user."""
        author = ctx.author
        guild = ctx.guild
        await self.permissions.admin_role_check(ctx, guild)
        log_channel = await self.permissions.log_channel_check(guild)
        model = await WarningsModel.filter(
            guild_id=guild.id, member_id=member.id
        ).delete()
        await ctx.send(f"Cleared Warnings of **{member}**")
        embed = Embed(
            color=Color.green(),
            timestamp=datetime.utcnow(),
            description=f":warning: Cleared Warnings of \n**{member} [ID {member.id}]**",
        )
        embed.set_author(name=f"{author} [ID {author.id}]", icon_url=author.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)
        await log_channel.send(embed=embed)


def setup(bot: Bot) -> None:
    """Setup function for the Cog"""
    bot.add_cog(Warnings(bot))
