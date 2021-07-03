from modules.imports import *
from pathlib import Path
from dotenv import load_dotenv
from tatsu.wrapper import ApiWrapper

load_dotenv()
env_path = Path(".") / ".env"
load_dotenv(dotenv_path = env_path)

TATSU_KEY = os.getenv("TATSU_API_TOKEN")

class TatsuIntegration(Cog):

    def __init__(self, client):
        self.client = client
    

    @command(name="rank")
    async def tatsu_rank_command(self, ctx, member:Optional[Member]):
        guild = ctx.guild
        author = ctx.author
        member = member or author
        wrapper = ApiWrapper(key=TATSU_KEY)
        result = await wrapper.get_member_ranking(guild.id, member.id)

        embed = Embed(
            color = Color.blurple(),
            timestamp = datetime.utcnow(),
            description = f"**Member** - {member}\n **Server Rank** - #{result.rank}\n**Server Score** - {result.score}"
        )
        embed.set_author(name=f"Viewing rank • [  {author} ]", icon_url=member.avatar_url)
        await ctx.send(embed=embed)

    

    




def setup(client):
    client.add_cog(TatsuIntegration(client))