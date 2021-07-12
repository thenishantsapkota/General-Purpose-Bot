from datetime import date, timedelta
from io import BytesIO
from re import A
from typing import Text
from cogs.help import Help


import pytz

from models import ModerationRoles, MuteModel, PrefixModel, WarnModel
from modules.imports import *
from modules.permissions import *

emojis = ["🔨", "👢", "🔇", "🔊", "❌"]


class NotEnoughPermissions(commands.CommandError):
    pass


time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
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


class Moderation(Cog):
    def __init__(self, client):
        self.client = client

    @command(name="mute", aliases=["silence"], brief="Mute a member from the server.")
    # @commands.has_permissions(manage_messages=True)
    async def mute_command(
        self,
        ctx,
        members: Greedy[Member],
        time: TimeConverter,
        *,
        reason: Optional[str] = "No Reason Specified.",
    ):
        """Mute a member from the server."""
        author = ctx.author
        guild = ctx.guild
        staffrole = (await fetchRoleData(guild)).get("staffrole")
        if not (
            await has_permissions(author, "manage_messages")
            or await rolecheck(author, staffrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        unmutes = []
        for member in members:
            if ctx.author.top_role > member.top_role:
                if muted_role not in member.roles:
                    guild = ctx.guild
                    author = ctx.author
                    logChannel = discord.utils.get(
                        guild.text_channels, name="zorander-logs"
                    )
                    if logChannel is None:
                        logChannel = await guild.create_text_channel("zorander-logs")
                        await logChannel.set_permissions(
                            guild.default_role, view_channel=False, send_messages=False
                        )

                    if not muted_role:
                        muted_role = await guild.create_role(name="Muted")

                        for channel in guild.channels:
                            await channel.set_permissions(
                                muted_role,
                                speak=False,
                                send_messages=False,
                                read_message_history=True,
                            )
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
                        description=f"**:mute: Muted {member} [ID {member.id}]\nTime: {time}s**",
                        color=Color.red(),
                        timestamp=datetime.utcnow(),
                    )
                    embed.set_author(
                        name=f"{author} [ID {author.id}]",
                        icon_url=author.avatar_url,
                    )
                    embed.add_field(name="Reason", value=reason)
                    embed.set_thumbnail(url=member.avatar_url)
                    await logChannel.send(embed=embed)
                    await ctx.send(f":mute: Muted `{member.name}` for {time}s.")

                    if time:
                        unmutes.append(member)
                else:
                    await ctx.send("Member is already muted.", delete_after=10)
            else:
                await ctx.send(
                    "You cannot run moderation actions on the users on same rank as you or higher than you.",
                    delete_after=10,
                )
        if len(unmutes):
            await asyncio.sleep(time)
            await self.unmute_handler(ctx, members)

    @Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(5)
        models = MuteModel.all()
        async for model in models:
            asyncio.create_task(self.mute_handler(model))

    async def mute_handler(self, model: MuteModel):
        utc = pytz.UTC
        localized_mutetime = model.time
        localized_nowtime = utc.localize(datetime.now())
        if localized_mutetime > localized_nowtime:
            remaining_time = (localized_mutetime - localized_nowtime).total_seconds()
            await asyncio.sleep(remaining_time)
            await self.mute_handler_get(model)
            # print("Success")
            return
        await self.mute_handler_get(model)
        # print("Sucess - A")

    async def mute_handler_get(self, model: MuteModel):
        guild = self.client.get_guild(model.guild_id)
        member = guild.get_member(model.member_id)
        logChannel = discord.utils.get(guild.text_channels, name="zorander-logs")
        role_ids = model.role_id
        roles = [guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]
        await member.edit(roles=roles)
        await model.delete()
        embed = Embed(
            description=f"**:loud_sound: Unmuted {member} [ID {member.id}]**",
            color=Color.green(),
            timestamp=datetime.utcnow(),
        )
        embed.set_author(
            name=f"{self.client.user} [ID {self.client.user.id}]",
            icon_url=self.client.user.avatar_url,
        )
        embed.add_field(name="Reason", value="Mute Duration Expired.")
        embed.set_thumbnail(url=member.avatar_url)
        await logChannel.send(embed=embed)

    # @command(name="test")
    # async def test(self,ctx, member:Member):
    #     if ctx.guild.premium_subscriber_role in member.roles:
    #         await ctx.send("Has the role")
    #         return
    #     await ctx.send("Doesn't have the role.")

    @command(
        name="unmute", aliases=["unsilence"], brief="Unmute a member from the server."
    )
    # @commands.has_permissions(manage_messages=True)
    async def unmute(
        self,
        ctx,
        members: Greedy[Member],
        *,
        reason: Optional[str] = "No reason provided.",
    ):
        """Unmute a member from the server."""
        modrole = (await fetchRoleData(ctx.guild)).get("modrole")
        if not (
            await has_permissions(ctx.author, "kick_members")
            or await rolecheck(ctx.author, modrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )

        if not len(members):
            await ctx.send("One or more required arguments are missing.")

        else:
            await self.unmute_handler(ctx, members, reason=reason)

    async def unmute_handler(self, ctx, members, *, reason="Mute Duration Expired!"):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        guild = ctx.guild
        author = ctx.author
        for member in members:
            if muted_role in member.roles:
                logChannel = discord.utils.get(
                    guild.text_channels, name="zorander-logs"
                )
                if logChannel is None:
                    logChannel = await guild.create_text_channel("zorander-logs")
                    await logChannel.set_permissions(
                        guild.default_role, view_channel=False, send_messages=False
                    )
                model = await MuteModel.get_or_none(
                    guild_id=guild.id, member_id=member.id
                )
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
                await logChannel.send(embed=embed)
                await ctx.send(f":loud_sound: Unmuted `{member.name}`.")
            else:
                pass

    @command(name="kick", brief="Kick the member from the server.")
    # @commands.has_permissions(kick_members=True)
    async def kick_command(
        self,
        ctx,
        members: Greedy[Member],
        *,
        reason: Optional[str] = "No reason provided",
    ):
        """Kick the member from the server."""
        author = ctx.author
        guild = ctx.guild
        modrole = (await fetchRoleData(guild)).get("modrole")
        if not (
            await has_permissions(author, "kick_members")
            or await rolecheck(author, modrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )
        logChannel = discord.utils.get(guild.text_channels, name="zorander-logs")
        for member in members:
            if author.top_role > member.top_role:
                if logChannel is None:
                    logChannel = await guild.create_text_channel("zorander-logs")
                    await logChannel.set_permissions(
                        guild.default_role, view_channel=False, send_messages=False
                    )
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
                await logChannel.send(embed=embed)
                await ctx.send(f":boot: Kicked `{member.name}.`")
            else:
                await ctx.send(
                    "You cannot use moderation commands on users on same rank or higher that you.",
                    delete_after=10,
                )

    @command(
        name="ban",
        aliases=["hammer"],
        brief="Bans the member from the server.",
    )
    # @commands.has_permissions(ban_members=True)
    async def ban_command(self, ctx, members: Greedy[User], *, reason):
        """Bans the member from the server."""
        author = ctx.author
        guild = ctx.guild
        modrole = (await fetchRoleData(guild)).get("modrole")
        if not (
            await has_permissions(author, "ban_members")
            or await rolecheck(author, modrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )
        logChannel = discord.utils.get(guild.text_channels, name="zorander-logs")
        for member in members:
            # if author.top_role > member.top_role:
            if logChannel is None:
                logChannel = await guild.create_text_channel("zorander-logs")
                await logChannel.set_permissions(
                    guild.default_role, view_channel=False, send_messages=False
                )
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
            await logChannel.send(embed=embed)
            await ctx.send(f":hammer: Banned `{member.name}.`")

        # else:
        #     await ctx.send(
        #             "You cannot use moderation commands on users on same rank or higher that you.",
        #             delete_after=10,
        #         )

    @command(name="unban", brief="Unban the user from the server.")
    # @commands.has_permissions(manage_guild=True)
    async def unban_command(
        self, ctx, user: User, *, reason: Optional[str] = "No reason specified."
    ):
        """Unban the user from the server."""
        author = ctx.author
        guild = ctx.guild
        modrole = (await fetchRoleData(guild)).get("modrole")
        if not (
            await has_permissions(author, "ban_members")
            or await rolecheck(author, modrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )
        logChannel = discord.utils.get(guild.text_channels, name="zorander-logs")
        if logChannel is None:
            logChannel = await guild.create_text_channel("zorander-logs")
            await logChannel.set_permissions(
                guild.default_role, view_channel=False, send_messages=False
            )
        await guild.unban(user, reason=reason)
        embed = Embed(
            color=Color.green(),
            timestamp=datetime.utcnow(),
            description=f"**:unlock: Unbanned {user} [ID {user.id}]**",
        )
        embed.set_author(
            name=f"{author} [ID {author.id}]",
            icon_url=author.avatar_url,
        )
        embed.add_field(name="Reason", value=reason)
        embed.set_thumbnail(url=user.avatar_url)
        await logChannel.send(embed=embed)
        await ctx.send(f":unlock: Unbanned `{user.name}`")

    @command(name="warn", brief="Warns the user.")
    # @commands.has_permissions(manage_messages=True)
    async def warn_command(self, ctx, members: Greedy[Member], *, reason):
        """Warns the user."""
        author = ctx.author
        guild = ctx.guild

        staffrole = (await fetchRoleData(guild)).get("staffrole")
        if not (
            await has_permissions(author, "manage_messages")
            or await rolecheck(author, staffrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )
        for member in members:
            logChannel = discord.utils.get(guild.text_channels, name="zorander-logs")
            if author.top_role > member.top_role:
                if logChannel is None:
                    logChannel = await guild.create_text_channel("zorander-logs")
                    await logChannel.set_permissions(
                        guild.default_role, view_channel=False, send_messages=False
                    )
                model = await WarnModel.create(
                    guild_id=guild.id, member_id=member.id, reason=reason
                )
                await model.save()
                warn_model = await WarnModel.filter(
                    guild_id=guild.id, member_id=member.id
                )

                if len(warn_model) > 7:
                    await member.kick(reason="Too Many Warnings")
                    embed = Embed(
                        color=Color.red(),
                        timestamp=datetime.utcnow(),
                        description=f"**:boot: Kicked {member} [ID {member.id}]**",
                    )
                    embed.set_author(
                        name=f"{self.client.user} [ID {self.client.user.id}]",
                        icon_url=self.client.user.avatar_url,
                    )
                    embed.add_field(name="Reason", value="Too Many Warnings")
                    embed.set_thumbnail(url=member.avatar_url)
                    await logChannel.send(embed=embed)
                    await ctx.send(f":boot: Kicked `{member.name}.`")

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
                await logChannel.send(embed=embed)
                await ctx.send(f":warning: Warned `{member.name}`")
            else:
                await ctx.send(
                    "You cannot use moderation commands on users on same rank or higher than you.",
                    delete_after=10,
                )

    @commands.group(invoke_without_command=True)
    async def warnings(self, ctx, member: Optional[Member]):
        guild = ctx.guild
        author = ctx.author
        staffrole = (await fetchRoleData(guild)).get("staffrole")
        if not (
            await has_permissions(author, "manage_messages")
            or await rolecheck(author, staffrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )
        # await ctx.send(f"Use `delete` or `clear` as arguments to delete or clear warnings.")
        member = member or author
        warn_model = await WarnModel.filter(guild_id=guild.id, member_id=member.id)

        warnings = "\n".join(
            [
                f" ```{i+1}. {model.reason}   [Warning ID - {model.id}]```"
                for (i, model) in enumerate(warn_model)
            ]
        )
        embed = Embed(
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
            description=warnings if len(warn_model) else "User hasn't been warned.",
        )
        embed.set_footer(text=f"Requested by {author.name}")
        embed.set_author(name=f"Warnings of {member.name}", icon_url=member.avatar_url)
        await ctx.send(embed=embed)

    @warnings.group(name="delete", brief="Delete a warning of a user.")
    # @commands.has_permissions(kick_members=True)
    async def delwarning_command(self, ctx, id: int):
        """Delete a warning of a user."""
        guild = ctx.guild
        author = ctx.author
        modrole = (await fetchRoleData(guild)).get("modrole")
        if not (
            await has_permissions(author, "kick_members")
            or await rolecheck(author, modrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )
        model = await WarnModel.get_or_none(guild_id=guild.id, id=id)
        await model.delete()
        await ctx.send("Done :ok_hand:")

    @warnings.group(name="clear", brief="Clear the warnings of the member.")
    # @commands.has_permissions(administrator=True)
    async def clw_command(self, ctx, member: Member):
        """Clear the warnings of the member."""
        author = ctx.author
        guild = ctx.guild
        adminrole = (await fetchRoleData(guild)).get("adminrole")
        if not (
            await has_permissions(author, "kick_members")
            or await rolecheck(author, adminrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )
        model = await WarnModel.filter(guild_id=guild.id, member_id=member.id).delete()
        embed = Embed(color=Color.green())
        embed.set_author(
            name=f"Warnings of {member.name} cleared successfully by {author.name}.",
            icon_url=member.avatar_url,
        )
        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def role(self, ctx):
        embed = Embed(
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
        )
        embed.add_field(
            name=f"**Arguments**",
            value=f"`admin` - Set admin role for the server.\n\n`mod` - Set mod role for the server\n\n`staff` - Set staff role for the server.\n\n`give` - Give a role to the user.\nExample: `role give <member> <role>`\n\n`take` - Take a role from the user.\nExample: `role take <member> <role>`",
        )
        embed.set_author(
            name=f"Help with role command.", icon_url=self.client.user.avatar_url
        )
        embed.set_footer(text=f"Invoked by {ctx.author}")
        await ctx.send(embed=embed)

    @role.group(name="admin")
    @commands.has_permissions(administrator=True)
    async def adminroleset(self, ctx, role: Role):
        guild = ctx.guild
        author = ctx.author

        if role in ctx.guild.roles:
            model, _ = await ModerationRoles.get_or_create(guild_id=guild.id)
            model.admin_role = role.id
            await model.save()
            embed = Embed(
                title="Admin Role",
                description=f"The admin role  for {ctx.guild.name} has been set to {role.mention}",
                timestamp=datetime.utcnow(),
                color=Color.blurple(),
            )
            await ctx.send(embed=embed)

    @role.group(name="mod")
    @commands.has_permissions(administrator=True)
    async def modroleset(self, ctx, role: Role):
        guild = ctx.guild
        author = ctx.author

        if role in ctx.guild.roles:
            model, _ = await ModerationRoles.get_or_create(guild_id=guild.id)
            model.mod_role = role.id
            await model.save()
            embed = Embed(
                title="Moderator Role",
                description=f"The mod role  for {ctx.guild.name} has been set to {role.mention}",
                timestamp=datetime.utcnow(),
                color=Color.blurple(),
            )
            await ctx.send(embed=embed)

    @role.group(name="staff")
    @commands.has_permissions(administrator=True)
    async def staffroleset(self, ctx, role: Role):
        guild = ctx.guild
        author = ctx.author

        if role in ctx.guild.roles:
            model, _ = await ModerationRoles.get_or_create(guild_id=guild.id)
            model.staff_role = role.id
            await model.save()
            embed = Embed(
                title="Staff Role",
                description=f"The staff role  for {ctx.guild.name} has been set to {role.mention}",
                timestamp=datetime.utcnow(),
                color=Color.blurple(),
            )
            await ctx.send(embed=embed)

    @role.group(name="give", aliases=["add"], brief="Add a role to the user.")
    # @commands.has_permissions(administrator=True)
    async def giverole_command(self, ctx, member: Optional[Member], *, role: Role):
        """Add a role to the user."""
        author = ctx.author
        guild = ctx.guild
        adminrole = (await fetchRoleData(guild)).get("adminrole")
        if not (
            await has_permissions(author, "administrator")
            or await rolecheck(author, adminrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )
        member = member or ctx.author
        if role in guild.roles:
            await member.add_roles(role, reason=f"Invoked by {author}")
            embed = Embed(
                color=role.color,
                timestamp=datetime.utcnow(),
                description=f"**Role Added** \n {role.name}",
            )
            embed.set_author(
                name=f"Updated roles for {member}", icon_url=member.avatar_url
            )
            embed.set_footer(text=f"Command Invoked by {author}")
            await ctx.send(embed=embed)

    @role.group(name="take", aliases=["remove"], brief="Remove a role from the user.")
    # @commands.has_permissions(administrator=True)
    async def takerole_command(self, ctx, member: Optional[Member], *, role: Role):
        """Remove a role from the user"""
        author = ctx.author
        guild = ctx.guild
        adminrole = (await fetchRoleData(guild)).get("adminrole")
        if not (
            await has_permissions(author, "administrator")
            or await rolecheck(author, adminrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )
        member = member or ctx.author
        if role in guild.roles:
            await member.remove_roles(role, reason=f"Invoked by {author}")
            embed = Embed(
                color=role.color,
                timestamp=datetime.utcnow(),
                description=f"**Role Removed** \n {role.name}",
            )
            embed.set_author(
                name=f"Updated roles for {member}", icon_url=member.avatar_url
            )
            embed.set_footer(text=f"Command Invoked by {author}")
            await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def channel(self, ctx):
        guild = ctx.guild
        author = ctx.author
        # channel = channel or ctx.channel
        modrole = (await fetchRoleData(guild)).get("modrole")
        if not (
            await has_permissions(author, "manage_channels")
            or await rolecheck(author, modrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )
        embed = Embed(
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
        )
        embed.add_field(
            name=f"**Arguments**",
            value=f"`lock` - Lock a specific channel.\nExample: `channel lock #general(optional)`\n\n`unlock` - Unlock a specific channel.\nExample: `channel unlock #general(optional)`",
        )
        embed.set_author(
            name=f"Help with channel command.", icon_url=self.client.user.avatar_url
        )
        embed.set_footer(text=f"Invoked by {ctx.author}")
        await ctx.send(embed=embed)

    @channel.group(name="lock")
    async def lockchannel_command(self, ctx, channel: Optional[TextChannel]):
        """Lock the channel provided"""
        guild = ctx.guild
        author = ctx.author
        channel = channel or ctx.channel
        modrole = (await fetchRoleData(guild)).get("modrole")
        if not (
            await has_permissions(author, "manage_channels")
            or await rolecheck(author, modrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )
        model = await ModerationRoles.get_or_none(guild_id=guild.id)
        staff_role = discord.utils.get(
            guild.roles, id=(0 if model is None else model.staff_role)
        )
        if staff_role is None:
            await ctx.send(
                f"Please set a staff role using `staffroleset <roleid>` before using lockchannel command."
            )
            return
        overwrite_staff = channel.overwrites_for(staff_role)
        overwrite_default = channel.overwrites_for(guild.default_role)
        overwrite_default.send_messages = False
        overwrite_staff.send_messages = True
        await channel.set_permissions(guild.default_role, overwrite=overwrite_default)
        await channel.set_permissions(staff_role, overwrite=overwrite_staff)
        embed = Embed(
            title="Lock Channel",
            description="🔒 Channel has been locked!",
            color=Color.red(),
        )
        await ctx.send(embed=embed)

    @channel.group(name="unlock", brief="Unlock the channel provided.")
    # @commands.has_permissions(manage_channels=True)
    async def unlockchannel_command(self, ctx, channel: Optional[TextChannel]):
        """Unlock the channel provided."""
        guild = ctx.guild
        channel = channel or ctx.channel
        author = ctx.author
        modrole = (await fetchRoleData(guild)).get("modrole")
        if not (
            await has_permissions(author, "manage_channels")
            or await rolecheck(author, modrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )

        model = await ModerationRoles.get_or_none(guild_id=guild.id)
        staff_role = discord.utils.get(
            guild.roles, id=(0 if model is None else model.staff_role)
        )
        if staff_role is None:
            await ctx.send(
                f"Please set a staff role using `staffroleset <roleid>` before using unlockchannel command."
            )
            return
        overwrite_staff = channel.overwrites_for(staff_role)
        overwrite_default = channel.overwrites_for(guild.default_role)
        overwrite_default.send_messages = None
        overwrite_staff.send_messages = None
        await channel.set_permissions(guild.default_role, overwrite=overwrite_default)
        await channel.set_permissions(staff_role, overwrite=overwrite_staff)
        embed = Embed(
            title="Unlock Channel",
            description="🔓 Channel has been unlocked!",
            color=Color.green(),
        )
        await ctx.send(embed=embed)

    @commands.group(
        name="lockdown", invoke_without_subcommand=True, brief="Lockdown the server."
    )
    # @commands.has_permissions(manage_channels=True)
    async def lockdown_command(self, ctx):
        """Lockdown the server."""
        author = ctx.author
        guild = ctx.guild
        modrole = (await fetchRoleData(guild)).get("modrole")
        if not (
            await has_permissions(author, "manage_channels")
            or await rolecheck(author, modrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )
        embed = Embed(
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
        )
        embed.add_field(
            name=f"**Arguments**",
            value=f"`start` - Start the server lockdown.\n\n`end` - End the server lockdown.",
        )
        embed.set_author(
            name=f"Help with lockdown command.", icon_url=self.client.user.avatar_url
        )
        embed.set_footer(text=f"Invoked by {ctx.author}")
        await ctx.send(embed=embed)

    @lockdown_command.command(name="start")
    async def startlockdown(self, ctx):
        guild = ctx.guild
        perms_default, perms_staff, staff_role = await self.get_permissions(ctx)

        perms_default.send_messages = False
        perms_default.connect = False
        perms_staff.send_messages = True
        await guild.default_role.edit(permissions=perms_default)
        await staff_role.edit(permissions=perms_staff)
        embed = discord.Embed(
            title="Lockdown",
            description=f"🔒 Server has been locked down!",
            color=Color.red(),
        )
        await ctx.send(embed=embed)

    @lockdown_command.command(name="end")
    async def endlockdown(self, ctx):
        guild = ctx.guild
        perms_default, perms_staff, staff_role = await self.get_permissions(ctx)

        perms_default.send_messages = True
        perms_default.connect = True
        perms_staff.send_messages = True
        await guild.default_role.edit(permissions=perms_default)
        await staff_role.edit(permissions=perms_staff)
        embed = discord.Embed(
            title="Lockdown",
            description=f"🔓 Server has been unlocked!",
            color=Color.green(),
        )
        await ctx.send(embed=embed)

    async def get_permissions(self, ctx):
        guild = ctx.guild
        model = await ModerationRoles.get_or_none(guild_id=guild.id)
        staff_role = discord.utils.get(
            guild.roles, id=(0 if model is None else model.staff_role)
        )
        if staff_role is None:
            await ctx.send(
                f"Please set a staff role using `staffroleset <roleid>` before using lockdown command."
            )
            return
        perms_default = guild.default_role.permissions
        perms_staff = staff_role.permissions
        return (perms_default, perms_staff, staff_role)

    @command(name="slowmode", brief="Add slowmode to the channel you invoke it in.")
    # @commands.has_permissions(manage_channels=True)
    async def slowmode_command(self, ctx, channel: Optional[TextChannel], seconds: int):
        """Add slowmode to the channel you invoke it in."""
        author = ctx.author
        guild = ctx.guild
        modrole = (await fetchRoleData(guild)).get("modrole")
        if not (
            await has_permissions(author, "manage_channels")
            or await rolecheck(author, modrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )
        channel = channel or ctx.channel
        await channel.edit(slowmode_delay=seconds)
        description = f"Set the slowmode delay in this channel to {seconds} seconds."
        embed = Embed(color=Color.blurple(), timestamp=datetime.utcnow())
        embed.set_footer(text=f"Command Invoked by {author}")
        embed.set_author(
            name=description if seconds != 0 else "Slowmode disabled in this channel.",
            icon_url=author.avatar_url,
        )
        await ctx.send(embed=embed)

    @command(name="members")
    async def members_in_role(self, ctx, role: Role):
        members = []
        guild = ctx.guild
        author = ctx.author
        staffrole = (await fetchRoleData(guild)).get("staffrole")
        if not (
            await has_permissions(author, "manage_messages")
            or await rolecheck(author, staffrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )
        for member in guild.members:
            if role in member.roles:
                members.append(member.mention)

        members_list = "\n".join(members[:15])
        embed = Embed(
            color=Color.blurple(), timestamp=datetime.utcnow(), description=members_list
        )
        embed.set_author(name=f"Members in {role}")
        embed.set_footer(text=f"Invoked by {author}")
        await ctx.send(embed=embed)

    # emoji section start
    @commands.group(invoke_without_command=True)
    async def emoji(self, ctx):
        embed = Embed(
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
        )
        embed.add_field(
            name=f"**Arguments**",
            value=f"`create` - Create an emoji from a emoji url.\nExample: `emoji create <url> <name>`\n\n`rename` - Rename an emoji from the server.\nExample : `emoji rename <emoji> <new_name>`\n\n`delete` - Delete an emoji from the server.\nExample : `emoji delete <emoji>`",
        )
        embed.set_author(
            name=f"Help with emoji command.", icon_url=self.client.user.avatar_url
        )
        embed.set_footer(text=f"Invoked by {ctx.author}")
        await ctx.send(embed=embed)

    @emoji.group(name="create", aliases=["addem"], brief="Add an emote to the server.")
    @commands.has_permissions(manage_emojis=True)
    async def createemoji(self, ctx, url: str, *, name):
        """Add an emote to the server using the url of the emote."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                try:
                    if r.status in range(200, 299):
                        emj = BytesIO(await r.read())
                        bytes = emj.getvalue()
                        emoji = await ctx.guild.create_custom_emoji(
                            image=bytes, name=name
                        )
                        await ctx.send(f"Emote sucessfully created | {emoji}")
                    else:
                        await ctx.send(f"Error making request | Response: {r.status}")
                except discord.HTTPException:
                    await ctx.send("File size may be too big.")

    @emoji.group(
        name="rename", aliases=["renameem"], brief="Rename the emoji of the server."
    )
    @commands.has_permissions(manage_emojis=True)
    async def renameemoji(self, ctx, emoji: discord.Emoji, *, name):
        """Rename the emoji of the server."""
        await ctx.send(f"{emoji} | Emote name changed to `{name}`")
        await emoji.edit(name=name, reason="Emoji Name Edit")

    @emoji.group(
        name="delete", aliases=["delem"], brief="Delete an emoji from the server."
    )
    @commands.has_permissions(manage_emojis=True)
    async def deleteemoji(self, ctx, emoji: discord.Emoji):
        """Delete an emoji from the server."""
        await ctx.send(f"{emoji} | Emote deleted sucessfully.")
        await emoji.delete()

    # emoji section end

    @command(
        name="changeprefix",
        aliases=["chp"],
        brief="Changes the prefix of the bot in the server.",
    )
    @commands.has_permissions(administrator=True)
    async def changeprefix_command(self, ctx, prefix: Optional[str]):
        """Changes the prefix of the bot in the server."""
        prefix = prefix or ">"
        model = await PrefixModel.get_or_none(guild_id=ctx.guild.id)
        model.prefix = prefix
        await model.save()
        embed = Embed(
            title="Prefix Changed",
            description=f"Prefix for {ctx.guild.name} has been changed to `{prefix}`",
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
        )
        await ctx.send(embed=embed)

    # @command(name="modmenu")
    # async def modmenu_command(self, ctx, member:Member):
    #     embed = Embed(
    #         color = Color.blurple(),
    #         description = f":hammer: - **Ban**\n:boot: - **Kick**\n:mute: - **Mute**\n:loud_sound: - **Unmute**\n:x: - **Close Menu**"
    #     )
    #     embed.set_author(name=f"{member} - Mod Menu")
    #     msg = await ctx.send(embed=embed)

    #     for i in range(len(emojis)):
    #         await msg.add_reaction(emojis[i])

    # @Cog.listener()
    # async def on_raw_reaction_add(self, payload):
    #     if (payload.member.id != self.client.user.id and str(payload.emoji) in emojis):
    #         print(payload.message_id)


def setup(client):
    client.add_cog(Moderation(client))
