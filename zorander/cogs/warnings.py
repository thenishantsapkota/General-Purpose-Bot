from logging import warn
import discord
from discord.channel import TextChannel
from discord.ext import commands
from discord import Color, Member, User, Embed
from datetime import datetime
from discord.ext.commands import Cog, command, Greedy

from zorander.core.models import WarnModel
from zorander.utils.permissions import Permissions
from zorander.cogs.mod import Mod


from zorander import Bot


class Warnings(Cog):
    def __init__(self, bot: Bot) -> None:
        """Init Function for the Cog"""
        self.bot = bot
        self.permissions = Permissions()
        self.mod = Mod(bot)

    async def warning_count(self, ctx: commands.Context, member: Member) -> None:
        """Function that checks for amount of warnings"""
        warn_model = await WarnModel.filter(guild_id=ctx.guild.id, member_id=member.id)
        if len(warn_model) in list(range(5, 8)):
            await self.mod.mute_handler(ctx, [member], 600, "Warning Count : 5")
        if len(warn_model) in list(range(8, 10)):
            await self.mod.mute_handler(ctx, [member], 21600, "Warning Count : 8")
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
            model = await WarnModel.create(
                guild_id=guild.id, member_id=member.id, reason=reason
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


def setup(bot: Bot) -> None:
    """Setup function for the Cog"""
    bot.add_cog(Warnings(bot))
