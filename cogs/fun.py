import random

import aiohttp

from modules.imports import *


class Fun(Cog):
    def __init__(self, client):
        self.client = client

    @command(name="catfact", brief="Returns a cat fact.")
    async def catfact_command(self, ctx):
        """Returns a cat fact."""
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
        """Returns a dog fact."""
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

    @command(name="iqcheck", brief="Return the IQ Value of the member.")
    async def iqcheck_command(self, ctx, member: Optional[Member]):
        """Return the IQ Value of the member."""
        member = member or ctx.author
        integer = random.randint(1, 200)
        await ctx.send(f"**{member}'s IQ is {integer}.**")

    @command(name="wink", brief="Wink at the member provided.")
    async def wink_command(self, ctx, member: Member):
        """Wink at the member provided."""
        if member is ctx.author:
            await ctx.send("You cannot wink at yourself. That's weird.")
            return
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/animu/wink") as resp:
                wink = await resp.json()
                wink_url = wink["link"]
        embed = Embed(color=Color.blurple(), timestamp=datetime.utcnow())
        embed.set_author(name=f"{ctx.author.name} winked at {member.name}.")
        embed.set_image(url=wink_url)
        await ctx.send(embed=embed)

    @command(name="pat", brief="Pat the member provided.")
    async def pat_command(self, ctx, member: Member):
        """Pat the member provided."""
        if member is ctx.author:
            await ctx.send("You cannot pat yourself. You lonely shit.")
            return
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/animu/pat") as resp:
                pat = await resp.json()
                pat_url = pat["link"]
        embed = Embed(color=Color.blurple(), timestamp=datetime.utcnow())
        embed.set_author(name=f"{ctx.author.name} patted {member.name}.")
        embed.set_image(url=pat_url)
        await ctx.send(embed=embed)

    @command(name="hug", brief="Hug the member provided.")
    async def hug_command(self, ctx, member: Member):
        """Hug the member provided."""
        if member is ctx.author:
            await ctx.send("You cannot hug yourself. You lonely shit.")
            return
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/animu/hug") as resp:
                hug = await resp.json()
                hug_url = hug["link"]
        embed = Embed(color=Color.blurple(), timestamp=datetime.utcnow())
        embed.set_author(name=f"{ctx.author.name} hugged {member.name}.")
        embed.set_image(url=hug_url)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Fun(client))
