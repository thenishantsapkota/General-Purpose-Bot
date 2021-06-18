from modules.imports import *
from models import PrefixModel


class Prefixes(Cog):
    def __init__(self, client):
        self.client = client

    @command(
        name="changeprefix",
        aliases=["chp"],
        description="Changes the prefix of the bot in the server.",
    )
    @commands.has_permissions(administrator=True)
    async def changeprefix_command(self, ctx, prefix: str):
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


def setup(client):
    client.add_cog(Prefixes(client))
