import random

import aiohttp

from modules.imports import *


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

    @command(name="iqcheck")
    async def iqcheck_command(self, ctx, member: Optional[Member]):
        member = member or ctx.author
        integer = random.randint(1, 200)
        await ctx.send(f"**{member}'s IQ is {integer}.**")

    @command(name="wink")
    async def wink_command(self, ctx, member: Member):
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

    @command(name="pat")
    async def pat_command(self, ctx, member: Member):
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

    @command(name="hug")
    async def hug_command(self, ctx, member: Member):
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

    @command(name="countryinfo")
    async def countryinfo_command(self, ctx, *, countryname: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://restcountries.eu/rest/v2/name/{countryname}"
            ) as resp:
                info = await resp.json()
                countryName = info[0]["name"]
                topLevelDomainn = info[0]["topLevelDomain"]
                topLevelDomain = ",".join(topLevelDomainn)
                alpha2Code = info[0]["alpha2Code"]
                callingCodesList = info[0]["callingCodes"]
                callingCodes = ",".join(callingCodesList)
                capital = info[0]["capital"]
                region = info[0]["region"]
                population = info[0]["population"]
                nativeName = info[0]["nativeName"]
                timeZonesList = info[0]["timezones"]
                timeZones = ",".join(timeZonesList)
                currencies = info[0]["currencies"]
                currency_code = currencies[0]["code"]
                currency_symbol = currencies[0]["symbol"]
                alternativeSpellingsList = info[0]["altSpellings"]
                alternativeSpellings = ",".join(alternativeSpellingsList)

        embed = Embed(
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
            description=f"**Name** - {countryName}\n**Top Level Domain** - {topLevelDomain}\n**Alpha2 Code** - {alpha2Code}\n**Calling Codes** - {callingCodes}\n**Capital** - {capital}\n **Region** - {region}\n**Population** - {population}\n**Native Name** - {nativeName}\n**Time Zones** - {timeZones}\n**Currency Code** - {currency_code}\n**Currency Symbol** - {currency_symbol}\n**Alternative Spellings** - {alternativeSpellings}",
        )
        embed.set_author(name=f"Info of {countryName}")
        embed.set_thumbnail(
            url=f"https://flagcdn.com/w80/{str(alpha2Code).lower()}.png")
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Fun(client))
