"""Module that helps in setting up moderation roles for the server."""
from operator import mod
from typing import Text

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
        """
        Checks if the provided member has required permissions.

        Parameters
        ----------
        member : Member
            Member that needs to be checked
        permission : str
            Permission that needs to be checked.

        Returns
        -------
        bool
            Returns a boolean value if the user has the certain permission.
        """
        if getattr(member.guild_permissions, permission, False):
            return True
        return False

    async def rolecheck(self, member: Member, role: Role) -> bool:
        """Function that checks if member has a certain role

        Parameters
        ----------
        member : Member
            Member that needs to be checked for roles.
        role : Role
            Role that needs to be checked

        Returns
        -------
        bool
            Returns a boolean value if the user has certain roles.
        """
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
        """
        Function that checks if member has the staff role for the guild

        Parameters
        ----------
        ctx : Context
            Context of the command invokation.
        guild : Guild
            Guild where the command was invoked in

        Raises
        ------
        NotEnoughPermissions
            Raise this error when the user doesn't have the staff role of the server.
        """
        staffrole = (await self.fetch_role_data(guild)).get("staffrole")
        if not (
            await self.has_permissions(ctx.author, "manage_messages")
            or await self.rolecheck(ctx.author, staffrole)
        ):
            raise NotEnoughPermissions(
                f"You don't have the required permissions or,\nYou don't have {staffrole.mention} role to run this command."
            )

    async def mod_role_check(self, ctx: Context, guild: Guild) -> None:
        """
        Function that checks if member has the mod role for the guild

        Parameters
        ----------
        ctx : Context
            Context of the command invokation.
        guild : Guild
            Guild where the command was invoked in

        Raises
        ------
        NotEnoughPermissions
            Raise this error when the user doesn't have the mod role of the server.
        """
        modrole = (await self.fetch_role_data(guild)).get("modrole")
        if not (
            await self.has_permissions(ctx.author, "kick_members")
            or await self.rolecheck(ctx.author, modrole)
        ):
            raise NotEnoughPermissions(
                f"You don't have the required permissions or,\nYou don't have {modrole.mention} role to run this command."
            )

    async def admin_role_check(self, ctx: Context, guild: Guild) -> None:
        """
        Function that checks if member has the admin role for the guild

        Parameters
        ----------
        ctx : Context
            Context of the command invokation.
        guild : Guild
            Guild where the command was invoked in

        Raises
        ------
        NotEnoughPermissions
            Raise this error when the user doesn't have the admin role of the server.
        """
        adminrole = (await self.fetch_role_data(guild)).get("adminrole")
        if not (
            await self.has_permissions(ctx.author, "manage_guild")
            or await self.rolecheck(ctx.author, adminrole)
        ):
            raise NotEnoughPermissions(
                f"You don't have the required permissions or,\nYou don't have {adminrole.mention} role to run this command."
            )

    async def log_channel_check(self, guild: Guild) -> TextChannel:
        """Function that check if the log channel exists, if not it creates one

        Returns
        -------
        TextChannel
            Log channel for the server.
        """
        log_channel = discord.utils.get(guild.text_channels, name="mod-logs")
        if log_channel is None:
            log_channel = await guild.create_text_channel("mod-logs")
            await log_channel.set_permissions(
                guild.default_role, view_channel=False, send_messages=False
            )
        return log_channel

    async def muted_role_check(self, guild: Guild) -> Role:
        """Function that checks for muted role in the server, if doesn't exist it creates it for you.

        Parameters
        ----------
        guild : Guild
            Guild where the command is invoked in.

        Returns
        -------
        Role
            Muted role of the server.
        """
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
        """Checks if command invokation author's top role is greater than member's top role or not

        Parameters
        ----------
        author : discord.Member
            Author of the command invoked.
        member : discord.Member
            Member Object

        Raises
        ------
        NotHigherRole
            Raises this error when author's top role is greater than member's top role
        """
        if not author.top_role > member.top_role:
            raise NotHigherRole(
                "You cannot run moderation actions on the users on same rank as you or higher than you."
            )
