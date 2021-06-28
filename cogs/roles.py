from modules.imports import *
from models import ModerationRoles


class NotEnoughPermissions(commands.CommandError):
    pass


class Roles(Cog):

    def __init__(self, client):
        self.client = client

    async def has_permissions(self, member: Member, permission: str):
        if getattr(member.guild_permissions, permission, False):
            return True
        return False

    async def rolecheck(self, member: Member, role: Role):
        if role in member.roles:
            return True
        return False

    async def fetchRoleData(self, guild: discord.Guild):
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

    @command(name="members")
    async def members_in_role(self, ctx, role: Role):
        members = []
        guild = ctx.guild
        author = ctx.author
        staffrole = (await self.fetchRoleData(guild)).get("staffrole")
        if not (
            await self.has_permissions(author, "manage_messages")
            or await self.rolecheck(author, staffrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )
        for member in guild.members:
            if role in member.roles:
                members.append(member.mention)

        members_list = "\n".join(members[:15])
        embed = Embed(
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
            description=members_list
        )
        embed.set_author(name=f"Members in {role}")
        embed.set_footer(text=f"Invoked by {author}")
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Roles(client))
