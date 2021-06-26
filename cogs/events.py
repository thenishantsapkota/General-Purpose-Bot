from models import OnMemberJoinModel, PrefixModel
from modules.imports import *


class Events(Cog):
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

    @Cog.listener()
    async def on_message(self, msg):
        if self.client.user.mentioned_in(msg) and "prefix" in msg.content:
            record = await PrefixModel.get_or_none(guild_id=msg.guild.id)
            prefix = ">" if not record.prefix else record.prefix
            embed = Embed(
                title="Prefix",
                description=f"The prefix for {msg.guild.name} is `{prefix}`.",
                color=Color.blurple(),
                timestamp=datetime.utcnow(),
            )
            await msg.channel.send(embed=embed)

    @Cog.listener()
    async def on_guild_join(self, guild):
        record, _ = await PrefixModel.get_or_create(guild_id=guild.id, prefix=">")
        welcome, _ = await OnMemberJoinModel.get_or_create(
            channel_id=0,
            guild_id=guild.id,
            welcome_message="Enjoy your stay here.",
            base_role_id=0,
        )
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
