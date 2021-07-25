import discord
from discord import Guild, Member, Role
from discord.ext import commands

from models import ModerationRoles


class NotEnoughPermissions(commands.CommandError):
    pass

class SetModerationRoles(commands.CommandError):
    pass


async def has_permissions(member: Member, permission: str):
    if getattr(member.guild_permissions, permission, False):
        return True
    return False


async def rolecheck(member: Member, role: Role):
    if role in member.roles:
        return True
    return False


async def fetchRoleData(guild: Guild):
    model = await ModerationRoles.get_or_none(guild_id=guild.id)
    if model is None:
        raise SetModerationRoles("""Please setup moderation roles before using any moderation commands.
        Use `role admin <roleid>`, `role mod <roleid>`, `role staff <roleid>` to set moderation roles.
        """)
    adminrole = discord.utils.get(guild.roles, id=model.admin_role)
    modrole = discord.utils.get(guild.roles, id=model.mod_role)
    staffrole = discord.utils.get(guild.roles, id=model.staff_role)
    coder_girls_lead = discord.utils.get(guild.roles, id=868748867661864990)
    roles = {
        "adminrole": adminrole,
        "modrole": modrole,
        "staffrole": staffrole,
        "codergirlslead": coder_girls_lead
    }
    return roles
