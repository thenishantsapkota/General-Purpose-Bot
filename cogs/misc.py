from datetime import date
from modules.imports import *


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

    @command(name="serverinfo")
    async def serverinfo_command(self, ctx):
        owner = str(ctx.guild.owner)
        id = str(ctx.guild.id)
        region = str(ctx.guild.region)
        memberCount = str(ctx.guild.member_count)
        textChannels = len(ctx.guild.text_channels)
        voiceChannels = len(ctx.guild.voice_channels)
        guildCreatedate = ctx.guild.created_at.strftime("%a, %#d %B %Y, %I:%M %p")

        embed = Embed(
            title=f"Info of {ctx.guild.name} Server",
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        fields = [
            ("Owner", owner, False),
            ("Server ID", id, False),
            ("Server Region", region.capitalize(), False),
            ("Member Count", memberCount, False),
            ("Text Channels", textChannels, False),
            ("Voice Channels", voiceChannels, False),
            ("Created on", guildCreatedate, False),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)

    @command(name="userinfo")
    async def userinfo_command(self, ctx, member: Optional[Member]):
        member = member or ctx.author
        member_avatar = member.avatar_url
        id = member.id
        name = member.name
        accountAge = member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")
        joinServerDate = member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")
        highestRole = member.top_role.mention

        embed = Embed(
            title=f"User Info - {member.name}",
            timestamp=datetime.utcnow(),
            color=Color.blurple(),
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        embed.set_thumbnail(url=member_avatar)
        fields = [
            ("ID", id, False),
            ("Name", f"{name} #{ctx.author.discriminator}", False),
            ("Account Created on", accountAge, False),
            ("Joined Server on", joinServerDate, False),
            ("Highest Role", highestRole, False),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Misc(client))
