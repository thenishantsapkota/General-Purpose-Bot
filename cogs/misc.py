from modules.imports import *


class Misc(Cog):

    def __init__(self, client):
        self.client = client
    
    @command(name="avatar", aliases=["av"], brief="Returns the member's avatar.")
    async def avatar_command(self, ctx, member:Optional[Member]):
        if not member:
            member = ctx.message.author
        avatarUrl = member.avatar_url
        embed = Embed(
            title = f"Avatar - {member.name}",
            timestamp = datetime.utcnow() ,
            color = Color.blurple()
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        embed.set_image(url=avatarUrl)
        await ctx.send(embed=embed)
    
    

    

def setup(client):
    client.add_cog(Misc(client))