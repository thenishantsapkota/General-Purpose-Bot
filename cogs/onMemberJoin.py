from typing import Text
from modules.imports import *
from db.db_welcome import *



class WelcomeMessage(Cog):
    def __init__(self, client):
        self.client = client

    @command()
    @commands.has_permissions(manage_guild=True)
    async def setwelcome(self, ctx, channel: TextChannel):
        session.query(WelcomeDB).filter(WelcomeDB.guild_id == ctx.guild.id).update(
            {WelcomeDB.channel_id: channel.id})
        session.commit()
        embed = Embed(
            title="Welcome Channel",
            description=f"The welcome channel for {ctx.guild.name} has been set to {channel.mention}",
            timestamp=datetime.utcnow(),
            color=Color.blurple()
        )
        await ctx.send(embed=embed)
    

    @command()
    @commands.has_permissions(manage_guild=True)
    async def setwelcomemessage(self, ctx, *, welcomeMessage:Optional[str]):
        default = "Enjoy your stay here."
        session.query(WelcomeDB).filter(WelcomeDB.guild_id == ctx.guild.id).update(
            {WelcomeDB.welcome_message: welcomeMessage if welcomeMessage else default})
        session.commit()
        embed = Embed(
            title="Welcome Message",
            description=f"The welcome message for {ctx.guild.name} has been set to `{welcomeMessage if welcomeMessage else default}`",
            timestamp=datetime.utcnow(),
            color=Color.blurple()
        )
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_member_join(self, member):
        default = "Enjoy your stay here."
        for r in session.query(WelcomeDB).filter(WelcomeDB.guild_id == member.guild.id).all():
            channel = self.client.get_channel(r.channel_id)
            guild = self.client.get_guild(r.guild_id)
            message = r.welcome_message
        try:
            if guild.get_member(member.id) is not None:
                embed = Embed(
                    title=f"Welcome to {guild.name}",
                    description=f"{member.name} joined the server.\n {message if message else default}",
                    color=Color.green(),
                    timestamp=datetime.utcnow()
                )
                embed.set_thumbnail(url = member.avatar_url)
                await channel.send(member.mention, embed=embed)
        except:
            print("Member not in server!")


def setup(client):
    client.add_cog(WelcomeMessage(client))
