from modules.imports import *
from db.db_prefix import *



class Prefixes(Cog):
    def __init__(self, client):
        self.client = client
    

    @command(name="changeprefix", aliases=["chp"], description = "Changes the prefix of the bot in the server.")
    @commands.has_permissions(administrator=True)
    async def changeprefix_command(self, ctx,_prefix:str):
        session.query(BotPrefix).filter(BotPrefix.guild_id == ctx.guild.id).update({BotPrefix.prefix_bot : _prefix})
        session.commit()
        session.flush()
        embed = Embed(
            title = "Prefix Changed",
            description = f"Prefix for {ctx.guild.name} has been changed to `{_prefix}`",
            color = Color.blurple(),
            timestamp = datetime.utcnow()
        )
        await ctx.send(embed = embed)
        session.rollback()


def setup(client):
    client.add_cog(Prefixes(client))