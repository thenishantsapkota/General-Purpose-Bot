from modules.imports import *
from models import WelcomeModel


class WelcomeMessage(Cog):
    def __init__(self, client):
        self.client = client

    @command()
    @commands.has_permissions(manage_guild=True)
    async def setwelcome(self, ctx, channel: Optional[TextChannel]):
        channel = channel or ctx.channel
        model = await WelcomeModel.get_or_none(guild_id=ctx.guild.id)
        model.channel_id = channel.id
        await model.save()
        embed = Embed(
            title="Welcome Channel",
            description=f"The welcome channel for {ctx.guild.name} has been set to {channel.mention if channel else None}",
            timestamp=datetime.utcnow(),
            color=Color.blurple(),
        )
        await ctx.send(embed=embed)

    @command()
    @commands.has_permissions(manage_guild=True)
    async def setwelcomemessage(self, ctx, *, welcomeMessage: Optional[str]):
        welcome = await WelcomeModel.get_or_none(guild_id=ctx.guild.id)
        welcome.welcome_message = welcomeMessage
        await welcome.save()
        embed = Embed(
            title="Welcome Message",
            description=f"The welcome message for {ctx.guild.name} has been set to `{welcomeMessage if welcomeMessage else default}`",
            timestamp=datetime.utcnow(),
            color=Color.blurple(),
        )
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_member_join(self, member):
        default = "Enjoy your stay here."
        query = await WelcomeModel.get_or_none(guild_id=member.guild.id)
        message = query.welcome_message
        guild = self.client.get_guild(query.guild_id)
        channel = self.client.get_channel(query.channel_id)
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
        except:
            print("Member not in server!")


def setup(client):
    client.add_cog(WelcomeMessage(client))
