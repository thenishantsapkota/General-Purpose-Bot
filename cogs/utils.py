from io import BytesIO

from models import PrefixModel
from modules.imports import *
from modules.permissions import *


class Utils(Cog):
    def __init__(self, client):
        self.client = client

    @command(
        name="send",
        aliases=["say"],
        brief="Send a message to the channel you specify in.",
    )
    @commands.has_permissions(administrator=True)
    async def send_command(self, ctx, channel: Optional[TextChannel], *, message: str):
        """Send a message to the channel you specify in."""
        channel = channel or ctx.channel
        await channel.send(message)
        await ctx.message.delete()

    @command(
        name="clean", aliases=["purge"], brief="Delete messages from certain channels."
    )
    async def clean_command(self, ctx, limit: Optional[int] = 10):
        """Delete messages from certain channels."""
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
        if limit <= 100:
            await ctx.message.delete()
            await ctx.channel.purge(limit=limit)
            await ctx.send(
                "History deleted, Use Incognito next time.:wink:", delete_after=10
            )
        else:
            await ctx.send(
                "I can only delete 100 messages at a time** :rage:", delete_after=5
            )

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
    

def setup(client):
    client.add_cog(Utils(client))
