from modules.imports import *
from models import MuteModel, WarnModel, ModLogsModel


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
    @commands.has_permissions(manage_messages=True)
    async def mute_command(
        self,
        ctx,
        members: Greedy[Member],
        time: TimeConverter,
        *,
        reason: Optional[str] = "No Reason Specified.",
    ):
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

                    role_ids = ",".join([str(r.id) for r in member.roles])
                    model, _ = await MuteModel.get_or_create(
                        guild_id=guild.id,
                        member_id=member.id,
                        time=time,
                        role_id=role_ids,
                    )
                    await model.save()

                    await member.edit(roles=[muted_role], reason="Muted the User")
                    embed = Embed(
                        description=f"**:mute: Muted {member.name} # {member.discriminator} [ID {member.id}]**",
                        color=Color.red(),
                        timestamp=datetime.utcnow(),
                    )
                    embed.set_author(
                        name=f"{author.name} # {author.discriminator} [ID {author.id}]",
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

    @command(
        name="unmute", aliases=["unsilence"], brief="Unmute a member from the server."
    )
    @commands.has_permissions(manage_messages=True)
    async def unmute(
        self,
        ctx,
        members: Greedy[Member],
        *,
        reason: Optional[str] = "No reason provided.",
    ):
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
                    description=f"**:loud_sound: Unmuted {member.name} # {member.discriminator} [ID {member.id}]**",
                    color=Color.green(),
                    timestamp=datetime.utcnow(),
                )
                embed.set_author(
                    name=f"{author.name} # {author.discriminator} [ID {author.id}]",
                    icon_url=author.avatar_url,
                )
                embed.add_field(name="Reason", value=reason)
                embed.set_thumbnail(url=member.avatar_url)
                await logChannel.send(embed=embed)
                await ctx.send(f":loud_sound: Unmuted `{member.name}`.")
            else:
                pass

    @command(name="kick", brief="Kick the member from the server.")
    @commands.has_permissions(kick_members=True)
    async def kick_command(
        self,
        ctx,
        members: Greedy[Member],
        *,
        reason: Optional[str] = "No reason provided",
    ):
        author = ctx.author
        guild = ctx.guild
        logChannel = discord.utils.get(
                    guild.text_channels, name="zorander-logs"
        )
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
                    description=f"**:boot: Kicked {member.name} # {member.discriminator} [ID {member.id}]**",
                )
                embed.set_author(
                    name=f"{author.name} # {author.discriminator} [ID {author.id}]",
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
    @command(name="ban",aliases=["hammer"], brief = "Bans the member from the server.",description = "Bans the member from the server.")
    @commands.has_permissions(ban_members = True)
    async def ban_command(self, ctx, members:Greedy[User],*,reason):
        author = ctx.author
        guild = ctx.guild
        logChannel = discord.utils.get(
                    guild.text_channels, name="zorander-logs"
                )
        for member in members:
            #if author.top_role > member.top_role:
            if logChannel is None:
                logChannel = await guild.create_text_channel("zorander-logs")
                await logChannel.set_permissions(
                    guild.default_role, view_channel=False, send_messages=False
                )
            await guild.ban(member, reason = reason)
            embed = Embed(
                color=Color.red(),
                timestamp=datetime.utcnow(),
                description=f"**:hammer: Banned {member.name} # {member.discriminator} [ID {member.id}]**",
            )
            embed.set_author(
                name=f"{author.name} # {author.discriminator} [ID {author.id}]",
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


    @command(name="unban",brief = "Unban the user from the server.")
    @commands.has_permissions(manage_guild = True)
    async def unban_command(self, ctx, user:User, *, reason:Optional[str]="No reason specified."):
        author = ctx.author
        guild = ctx.guild
        logChannel = discord.utils.get(
                    guild.text_channels, name="zorander-logs"
                )
        if logChannel is None:
            logChannel = await guild.create_text_channel("zorander-logs")
            await logChannel.set_permissions(
                guild.default_role, view_channel=False, send_messages=False
            )
        await guild.unban(user,reason=reason)
        embed = Embed(
            color=Color.green(),
            timestamp=datetime.utcnow(),
            description=f"**:unlock: Unbanned {user.name} # {user.discriminator} [ID {user.id}]**",
        )
        embed.set_author(
            name=f"{author.name} # {author.discriminator} [ID {author.id}]",
            icon_url=author.avatar_url,
        )
        embed.add_field(name="Reason", value=reason)
        embed.set_thumbnail(url=user.avatar_url)
        await logChannel.send(embed=embed)
        await ctx.send(f':unlock: Unbanned `{user.name}`')







def setup(client):
    client.add_cog(Moderation(client))
