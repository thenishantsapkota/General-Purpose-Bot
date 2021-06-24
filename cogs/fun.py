from modules.imports import *
import aiohttp

class Fun(Cog):

    def __init__(self, client):
        self.client = client

    @command(name="catfact", brief="Returns a cat fact.")
    async def catfact_command(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/facts/cat") as resp:
                cat_fact = await resp.json()
                fact = cat_fact["fact"]
        embed = Embed(
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
            description=f"```{fact}```",
        )
        embed.set_author(
            name="Here's a cat fact for you.", icon_url=ctx.author.avatar_url
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

    @command(name="dogfact", brief="Returns a dog fact.")
    async def dogfact_command(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/facts/dog") as resp:
                dog_fact = await resp.json()
                fact = dog_fact["fact"]
        embed = Embed(
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
            description=f"```{fact}```",
        )
        embed.set_author(
            name="Here's a dog fact for you.", icon_url=ctx.author.avatar_url
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)



def setup(client):
    client.add_cog(Fun(client))