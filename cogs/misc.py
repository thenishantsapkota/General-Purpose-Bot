from datetime import date
from modules.imports import *
import aiohttp


class Misc(Cog):
    def __init__(self, client):
        self.client = client

    @command(name="avatar", aliases=["av"], brief="Returns the member's avatar.")
    async def avatar_command(self, ctx, member: Optional[Member]):
        member = member or ctx.author
        avatarUrl = member.avatar_url
        embed = Embed(
            title=f"Avatar - {member.name}",
            timestamp=datetime.utcnow(),
            color=Color.blurple(),
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        embed.set_image(url=avatarUrl)
        await ctx.send(embed=embed)

    @command(name="serverinfo", brief="Returns some info about the guild.")
    async def serverinfo_command(self, ctx):
        owner = str(ctx.guild.owner.mention)
        id = str(ctx.guild.id)
        region = str(ctx.guild.region)
        memberCount = str(ctx.guild.member_count)
        textChannels = len(ctx.guild.text_channels)
        voiceChannels = len(ctx.guild.voice_channels)
        roles = len(ctx.guild.roles)
        guildCreatedate = ctx.guild.created_at.strftime("%a, %#d %B %Y, %I:%M %p")

        embed = Embed(
            title=f"Info of {ctx.guild.name} Server",
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        fields = [
            ("Server ID", id, True),
            ("Server Region", region.capitalize(), True),
            ("Owner", owner, True),
            ("Member Count", memberCount, True),
            ("Text Channels", textChannels, True),
            ("Voice Channels", voiceChannels, True),
            ("Role Count", roles, True),
            ("Created on", guildCreatedate, True),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)

    @command(name="userinfo", brief="See the info of the user.")
    async def userinfo_command(self, ctx, member: Optional[Member]):
        member = member or ctx.author
        member_avatar = member.avatar_url
        id = member.id
        name = member.name
        accountAge = member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")
        joinServerDate = member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")
        highestRole = member.top_role.mention

        info = "Server Owner" if ctx.guild.owner is ctx.author else "Member"

        embed = Embed(
            title=f"User Info - {member.name}",
            timestamp=datetime.utcnow(),
            color=Color.blurple(),
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        embed.set_thumbnail(url=member_avatar)
        fields = [
            ("ID", id, False),
            ("Name", f"{name} #{ctx.author.discriminator}", True),
            ("Highest Role", highestRole, True),
            ("Account Created on", accountAge, True),
            ("Joined Server on", joinServerDate, True),
            ("Additional Info", info, True),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)


    @command(name="ping", brief="Returns the bot latency.")
    async def ping_command(self, ctx):
        ping = int(self.client.latency * 1000)
        embed = Embed(
            title="Pong!", description=f"My ping is {ping}ms.", color=Color.green()
        )
        await ctx.send(embed=embed)

    @command(name="botinvite", brief="Returns the invite link of bot")
    async def botinvite_command(self, ctx):
        invite = f"https://discord.com/oauth2/authorize?client_id={self.client.user.id}&permissions=0&scope=bot"
        await ctx.send(invite)


def setup(client):
    client.add_cog(Misc(client))
