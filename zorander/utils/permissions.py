import discord
from discord import Guild, Member, Role
from discord.ext import commands
from discord.ext.commands.context import Context

from zorander.core.models import ModerationRoles


class NotEnoughPermissions(commands.CommandError):
    pass


class SetModerationRoles(commands.CommandError):
    pass


class Permissions:
    async def has_permissions(self, member: Member, permission: str):
        if getattr(member.guild_permissions, permission, False):
            return True
        return False

    async def rolecheck(self, member: Member, role: Role):
        if role in member.roles:
            return True
        return False

    async def fetch_role_data(self, guild: Guild):
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

    async def staff_role_check(self, ctx: Context, guild: Guild):
        staffrole = (await self.fetch_role_data(guild)).get("staffrole")
        if not (
            await self.has_permissions(ctx.author, "manage_messages")
            or await self.rolecheck(ctx.author, staffrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions to run this command."
            )

    async def mod_role_check(self, ctx: Context, guild: Guild):
        modrole = (await self.fetch_role_data(guild)).get("modrole")
        if not (
            await self.has_permissions(ctx.author, "kick_members")
            or await self.rolecheck(ctx.author, modrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )
