from models import MuteModel, OnMemberJoinModel
from modules.imports import *


class WelcomeMessage(Cog):
    def __init__(self, client):
        self.client = client

    @command(name="setwelcome", brief="Set a welcome channel for the server.")
    @commands.has_permissions(manage_guild=True)
    async def setwelcome_command(self, ctx, channel: Optional[TextChannel]):
        """Set a welcome channel for the server."""
        channel = channel or ctx.channel
        model = await OnMemberJoinModel.get_or_none(guild_id=ctx.guild.id)
        model.channel_id = channel.id
        await model.save()
        embed = Embed(
            title="Welcome Channel",
            description=f"The welcome channel for {ctx.guild.name} has been set to {channel.mention if channel else None}",
            timestamp=datetime.utcnow(),
            color=Color.blurple(),
        )
        await ctx.send(embed=embed)

    @command(name="setwelcomemessage", brief="Set welcome message for the server.")
    @commands.has_permissions(manage_guild=True)
    async def setwelcomemessage_command(self, ctx, *, welcomeMessage: Optional[str]):
        """Set welcome message for the server."""
        default = "Enjoy your stay here."
        welcome = await OnMemberJoinModel.get_or_none(guild_id=ctx.guild.id)
        welcome.welcome_message = welcomeMessage
        await welcome.save()
        embed = Embed(
            title="Welcome Message",
            description=f"The welcome message for {ctx.guild.name} has been set to `{welcomeMessage if welcomeMessage else default}`",
            timestamp=datetime.utcnow(),
            color=Color.blurple(),
        )
        await ctx.send(embed=embed)

    @command(name="baserole", brief="Set a base role for the server.")
    @commands.has_permissions(manage_guild=True)
    async def baserole_command(self, ctx, role: Role):
        """Set a base role for the server."""
        if role in ctx.guild.roles:
            model = await OnMemberJoinModel.get_or_none(guild_id=ctx.guild.id)
            model.base_role_id = role.id
            await model.save()
            embed = Embed(
                title="Base Role",
                description=f"The base role  for {ctx.guild.name} has been set to {role.mention}",
                timestamp=datetime.utcnow(),
                color=Color.blurple(),
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("No such roles could be found.")

    @Cog.listener()
    async def on_member_join(self, member):
        default = "Enjoy your stay here."
        mutedRole = discord.utils.get(member.guild.roles, name="Muted")
        muteQuery = await MuteModel.get_or_none(guild_id=member.guild.id)
        try:
            if muteQuery.member_id == member.id:
                await member.edit(roles=[mutedRole])
        except:
            pass
        query = await OnMemberJoinModel.get_or_none(guild_id=member.guild.id)
        message = query.welcome_message
        guild = self.client.get_guild(query.guild_id)
        channel = self.client.get_channel(query.channel_id)
        base_role = discord.utils.get(member.guild.roles, id=query.base_role_id)
        try:
            if guild.get_member(member.id) is not None:
                embed = Embed(
                    title=f"Welcome to {guild.name}",
                    description=f"{member.name} joined the server.\n {message if message else default}",
                    color=Color.green(),
                    timestamp=datetime.utcnow(),
                )
                embed.set_thumbnail(url=member.avatar_url)
                await channel.send(member.mention, embed=embed)
                try:
                    await member.add_roles(base_role)
                except:
                    pass
        except:
            pass


def setup(client):
    client.add_cog(WelcomeMessage(client))
