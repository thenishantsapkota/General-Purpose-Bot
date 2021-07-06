import asyncio
from discord.errors import Forbidden

from discord.ext.commands.errors import MissingPermissions
from discord.utils import find

from models import OnMemberJoinModel, PrefixModel
from modules.imports import *


class Events(Cog):
    """
    Cog to handle Events of the bot
    """

    def __init__(self, client):
        self.client = client

    @Cog.listener()
    async def on_ready(self):
        # print("Bot is Ready!")
        print(f"Logged in as  - {self.client.user.name} active in...")
        for i in self.client.guilds:
            print(f"{i.name}")
            await self.client.change_presence(
                activity=discord.Game(name="Visual Studio Code")
            )

    @command(name="prefix")
    async def on_message(self, ctx):
        record = await PrefixModel.get_or_none(guild_id=ctx.guild.id)
        prefix = ">" if not record else record.prefix
        embed = Embed(
            title="Prefix",
            description=f"The prefix for {ctx.guild.name} is `{prefix}`.",
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
        )
        await ctx.channel.send(embed=embed)

    @Cog.listener()
    async def on_guild_join(self, guild):
        record, _ = await PrefixModel.get_or_create(guild_id=guild.id, prefix=">")
        welcome, _ = await OnMemberJoinModel.get_or_create(
            channel_id=0,
            guild_id=guild.id,
            welcome_message="Enjoy your stay here.",
            base_role_id=0,
        )
        embed = Embed(
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
            description="**Thanks for adding me.:smile:\n\nBefore using the moderation commands, please set the Admin, Moderator, Staff Role using `adminroleset`, `modroleset`, `staffroleset` resepctively\n\nThe default prefix for this guild is > and if you wish to change it just run `chp <desired_prefix>` to change the prefix.\n\nGreetings :heart:**",
        )
        embed.set_author(name=f"{self.client.user} has joined {guild.name}")
        bot_entry = await guild.audit_logs(
            action=discord.AuditLogAction.bot_add
        ).flatten()
        await bot_entry[0].user.send(embed=embed)
        await welcome.save()
        await record.save()

    @Cog.listener()
    async def on_guild_remove(self, guild):
        record = await PrefixModel.get(guild_id=guild.id)
        await record.delete()
        welcome = await OnMemberJoinModel.get(guild_id=guild.id)
        await welcome.delete()


def setup(client):
    client.add_cog(Events(client))
