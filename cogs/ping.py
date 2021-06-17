from modules.imports import *


class Ping(Cog):

    def __init__(self, client):
        self.client = client
    
    @command(name="ping", brief="Returns the bot latency.")
    async def ping_command(self,ctx):
        ping = int(self.client.latency*1000)
        embed = Embed(
            title = "Pong!",
            description = f"My ping is {ping}ms.",
            color = Color.green()
        )
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Ping(client))