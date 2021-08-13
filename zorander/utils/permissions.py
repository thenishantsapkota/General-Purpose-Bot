"""Module that helps in setting up moderation roles for the server."""
import discord
from discord import Guild, Member, Role, TextChannel
from discord.ext import commands
from discord.ext.commands.context import Context

from zorander.core.models import ModerationRoles


class NotEnoughPermissions(commands.CommandError):
    """Class that raises errors when there is not enough permissions."""

    pass


class SetModerationRoles(commands.CommandError):
    """Class that raises errors when moderation roles are not setup"""

    pass

class NotHigherRole(commands.CommandError):
    """Class that raises errors when author's top role is lower than member's top role"""
    pass


class Permissions:
    """Custom class for setting guild perms."""

    async def has_permissions(self, member: Member, permission: str) -> bool:
        if getattr(member.guild_permissions, permission, False):
            return True
        return False

    async def rolecheck(self, member: Member, role: Role) -> bool:
        if role in member.roles:
            return True
        return False

    async def fetch_role_data(self, guild: Guild) -> dict:
        model = await ModerationRoles.get_or_none(guild_id=guild.id)
        if model is None:
            raise SetModerationRoles(
                """Please setup moderation roles before using any moderation commands.
            Use `role admin <roleid>`, `role mod <roleid>`, `role staff <roleid>` to set moderation roles.
            """
            )
        adminrole = discord.utils.get(guild.roles, id=model.admin_role)
        modrole = discord.utils.get(guild.roles, id=model.mod_role)
        staffrole = discord.utils.get(guild.roles, id=model.staff_role)
        roles = {
            "adminrole": adminrole,
            "modrole": modrole,
            "staffrole": staffrole,
        }
        return roles

    async def staff_role_check(self, ctx: Context, guild: Guild) -> None:
        staffrole = (await self.fetch_role_data(guild)).get("staffrole")
        if not (
            await self.has_permissions(ctx.author, "manage_messages")
            or await self.rolecheck(ctx.author, staffrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions to run this command."
            )

    async def mod_role_check(self, ctx: Context, guild: Guild) -> None:
        modrole = (await self.fetch_role_data(guild)).get("modrole")
        if not (
            await self.has_permissions(ctx.author, "kick_members")
            or await self.rolecheck(ctx.author, modrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )

    async def log_channel_check(self, guild: Guild) -> TextChannel:
        log_channel = discord.utils.get(guild.text_channels, name="mod-logs")
        if log_channel is None:
            log_channel = await guild.create_text_channel("mod-logs")
            await log_channel.set_permissions(
                guild.default_role, view_channel=False, send_messages=False
            )
        return log_channel

    async def muted_role_check(self, guild: Guild) -> Role:
        muted_role = discord.utils.get(guild.roles, name="Muted")
        if muted_role is None:
            muted_role = await guild.create_role(name="Muted")
            for channel in guild.channels:
                await channel.set_permissions(
                    muted_role,
                    speak=False,
                    send_messages=False,
                    read_message_history=True,
                )
        return muted_role
    
    def has_higher_role(self, author: discord.Member, member: discord.Member) -> None:
        if not author.top_role > member.top_role:
            raise NotHigherRole("You cannot run moderation actions on the users on same rank as you or higher than you.")
