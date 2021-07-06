import discord
from discord import Member, Role, Guild
from models import ModerationRoles


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
    if not model:
        return False
    adminrole = discord.utils.get(guild.roles, id=model.admin_role)
    modrole = discord.utils.get(guild.roles, id=model.mod_role)
    staffrole = discord.utils.get(guild.roles, id=model.staff_role)
    roles = {
        "adminrole": adminrole,
        "modrole": modrole,
        "staffrole": staffrole,
    }
    return roles
