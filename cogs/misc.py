import urllib.parse
from datetime import date
from io import BytesIO
from logging import log
from pathlib import Path

import aiohttp
from discord.ext import timers
from dotenv import load_dotenv

from models import ReputationPoints
from modules.imports import *

load_dotenv()
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

WEATHER_TOKEN = os.getenv("WEATHER_API_TOKEN")


time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k] * float(v)
            except KeyError:
                raise commands.BadArgument(
                    "{} is an invalid time-key! h/m/s/d are valid!".format(k)
                )
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))
        return time


class Misc(Cog):
    """
    Miscellaneous Commands of the Bot
    """

    def __init__(self, client):
        self.client = client

    @command(name="avatar", aliases=["av"], brief="Returns the member's avatar.")
    async def avatar_command(self, ctx, member: Optional[Member]):
        """Returns the member's avatar."""
        member = member or ctx.author
        avatarUrl = member.avatar_url
        embed = Embed(
            title=f"Avatar - {member.name}",
            timestamp=datetime.utcnow(),
            color=Color.blurple(),
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        embed.set_image(url=avatarUrl)
        await ctx.send(embed=embed)

    @command(name="serverinfo", brief="Returns some info about the guild.")
    async def serverinfo_command(self, ctx):
        """Returns some info about the guild."""
        owner = str(ctx.guild.owner.mention)
        id = str(ctx.guild.id)
        region = str(ctx.guild.region)
        memberCount = str(ctx.guild.member_count)
        textChannels = len(ctx.guild.text_channels)
        voiceChannels = len(ctx.guild.voice_channels)
        roles = len(ctx.guild.roles)
        guildCreatedate = ctx.guild.created_at.strftime("%a, %#d %B %Y, %I:%M %p")

        embed = Embed(
            title=f"Info of {ctx.guild.name} Server",
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        fields = [
            ("Server ID", id, True),
            ("Server Region", region.capitalize(), True),
            ("Owner", owner, True),
            ("Member Count", memberCount, True),
            ("Text Channels", textChannels, True),
            ("Voice Channels", voiceChannels, True),
            ("Role Count", roles, True),
            ("Created on", guildCreatedate, True),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)

    @command(name="userinfo", brief="See the info of the user.")
    async def userinfo_command(self, ctx, member: Optional[Member]):
        """See the info of the user."""
        member = member or ctx.author
        member_avatar = member.avatar_url
        id = member.id
        name = member.name
        accountAge = member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")
        joinServerDate = member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")
        highestRole = member.top_role.mention

        info = "Server Owner" if ctx.guild.owner is ctx.author else "Member"

        embed = Embed(
            title=f"User Info - {member.name}",
            timestamp=datetime.utcnow(),
            color=Color.blurple(),
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        embed.set_thumbnail(url=member_avatar)
        fields = [
            ("ID", id, False),
            ("Name", f"{name} #{ctx.author.discriminator}", True),
            ("Highest Role", highestRole, True),
            ("Account Created on", accountAge, True),
            ("Joined Server on", joinServerDate, True),
            ("Additional Info", info, True),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)

    @command(name="ping", brief="Returns the bot latency.")
    async def ping_command(self, ctx):
        """Returns the bot latency."""
        ping = int(self.client.latency * 1000)
        embed = Embed(
            title="Pong!", description=f"My ping is {ping}ms.", color=Color.green()
        )
        await ctx.send(embed=embed)

    @command(name="botinvite", brief="Returns the invite link of bot")
    async def botinvite_command(self, ctx):
        """Returns the invite link of bot"""
        invite = f"https://discord.com/oauth2/authorize?client_id={self.client.user.id}&permissions=0&scope=bot"
        await ctx.send(invite)

    @command(name="countryinfo", brief="Returns the info about the country provided.")
    async def countryinfo_command(self, ctx, *, countryname: str):
        """Returns the info about the country provided."""
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
            url=f"https://flagcdn.com/w80/{str(alpha2Code).lower()}.png"
        )
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    @command(name="githubinfo", brief="Returns github info of the username provided.")
    async def githubinfo_command(self, ctx, *, githubusername: str):
        """Returns github info of the username provided."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.github.com/users/{githubusername}"
            ) as resp:
                githubinfo = await resp.json()
                name = githubinfo["name"]
                avatar_url = githubinfo["avatar_url"]
                blog = githubinfo["blog"]
                location = githubinfo["location"]
                twitter_username = githubinfo["twitter_username"]
                publicrepos = githubinfo["public_repos"]
                followers = githubinfo["followers"]
                following = githubinfo["following"]
        embed = Embed(
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
            description=(
                f"**Name** - {name}\n**Blog URL** - {None if not blog else blog}\n**Location** - {location}\n**Twitter Username** - {twitter_username}\n **Public Repositories** - {publicrepos}\n**Followers** - {followers}\n**Following** - {following}"
            ),
        )
        embed.set_author(name=f"Github Profile info of username {githubusername}")
        if avatar_url is not None:
            embed.set_thumbnail(url=avatar_url)
        await ctx.send(embed=embed)

    @command(name="weather", brief="Returns the weather of the place provided.")
    async def weather_command(self, ctx, *, cityName: str):
        """Returns the weather of the place provided."""
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = base_url + "appid=" + WEATHER_TOKEN + "&q=" + cityName
        image = "https://icons-for-free.com/iconfiles/png/512/fog+foggy+weather+icon-1320196634851598977.png"
        async with aiohttp.ClientSession() as session:
            async with session.get(complete_url) as resp:
                data = await resp.json()
                main = data["main"]
                wind = data["wind"]
                weather = data["weather"]
                city = data["name"]
                temperature_in_celcius = int(main["temp"] - 273)
                feelslike_in_celcius = int(main["feels_like"] - 273)
                max_tempr = int(main["temp_max"] - 273)
                min_tempr = int(main["temp_min"] - 273)
                wind = data["wind"]
                speed_wind = wind["speed"]
                weather_description = str(weather[0]["description"]).title()
        embed = Embed(
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
            description=f"**Temperature** - {temperature_in_celcius} °C\n**Feels like** - {feelslike_in_celcius} °C\n**Maximum Temperature** - {max_tempr} °C\n**Minimum Temperature** - {min_tempr} °C\n**Description** - {weather_description}\n**Wind Velocity** - {speed_wind} km/h",
        )
        embed.set_author(name=f"Weather of {cityName.title()}")
        embed.set_thumbnail(url=image)
        await ctx.send(embed=embed)

    @command(name="carbon", brief="Returns the code snippet of the code you provide.")
    async def carbon_command(self, ctx, *, codeblock: str):
        """Returns the code snippet of the code you provide.(Currently doesn't work for C++ and C)"""
        regex = re.compile(r"(\w*)\s*(?:```)(\w*)?([\s\S]*)(?:```$)")
        matches = regex.findall(codeblock)
        if not matches:
            embed = Embed(color=Color.blurple())
            embed.set_author(
                name=f"Could not find codeblock.", icon_url=self.client.user.avatar_url
            )
            await ctx.send(embed=embed)
        code = matches[0][2]
        splitted_code = str(code).splitlines()
        codes = []
        codes = "%250A".join(splitted_code)
        # print(codes)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://carbonnowsh.herokuapp.com/?code={codes}&theme=monokai"
            ) as resp:
                file = BytesIO(await resp.read())
                bytes = file.getvalue()
            file = open("carbon.png", "wb")
            file.write(bytes)
            file.close()
            await ctx.send(file=discord.File(fp="carbon.png", filename="carbon.png"))
            os.remove("carbon.png")

    @command(name="c19", brief="Show the COVID-19 stats of the country provided.")
    async def c19_command(self, ctx, *, country: Optional[str]):
        """Show the COVID-19 stats of the country provided."""
        country = country or "nepal"
        logoUrl = "http://covidcp.org/images/logo-icononly.png"
        url = f"https://coronavirus-19-api.herokuapp.com/countries/{country}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                cntry = data["country"]
                cases = data["cases"]
                todayCases = data["todayCases"]
                deaths = data["deaths"]
                recovered = data["recovered"]
                active = data["active"]
        output = f"Total Cases - **{cases}** \n Cases Today - **{todayCases}** \nTotal Deaths - **{deaths}** \nActive Cases - **{active}** \nTotal Recovered - **{recovered}**"
        embed = Embed(
            color=Color.blurple(), timestamp=datetime.utcnow(), description=output
        )
        embed.set_author(name=f"COVID-19 Stats for {cntry}")
        embed.set_thumbnail(url=logoUrl)
        await ctx.send(embed=embed)

    def __init__(self, client):
        self.client = client

    async def _run_code(self, *, lang: str, code: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://emkc.org/api/v1/piston/execute",
                json={"language": lang, "source": code},
            ) as resp:
                return await resp.json()

    @command(name="compile", brief="Returns output of the code provided.")
    async def compile_command(self, ctx, *, codeblock: str):
        """
        Returns output of the code provided.
        """
        regex = re.compile(r"(\w*)\s*(?:```)(\w*)?([\s\S]*)(?:```$)")
        matches = regex.findall(codeblock)
        if not matches:
            embed = Embed(color=Color.blurple())
            embed.set_author(
                name=f"Could not find codeblock.", icon_url=self.client.user.avatar_url
            )
            await ctx.send(embed=embed)
        lang = matches[0][0] or matches[0][1]
        if not lang:
            embed = Embed(color=Color.blurple())
            embed.set_author(
                name=f"Could not find language hinted in the codeblock.",
                icon_url=self.client.user.avatar_url,
            )
        code = matches[0][2]
        result = await self._run_code(lang=lang, code=code)
        await self._send_result(ctx, result)

    async def _send_result(self, ctx, result: dict):
        if "message" in result:
            return await ctx.send(
                embed=Embed(
                    title="Error", description=result["message"], color=Color.red()
                )
            )
        output = result["output"]
        embed = Embed(timestamp=datetime.utcnow(), color=Color.green())
        output = output[:500]
        shortened = len(output) > 500
        lines = output.splitlines()
        shortened = shortened or (len(lines) > 15)
        output = "\n".join(lines[:15])
        output += shortened * "\n\n**Output shortened**"
        embed.set_author(
            name=f"Your code was in  {str(result['language']).capitalize()}.",
            icon_url=ctx.author.avatar_url,
        )
        embed.add_field(name="Output", value=f"`{output}`" or "**<No output>**")
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.message.add_reaction("<a:loading:856179279292006430>")
        await asyncio.sleep(2)
        await ctx.message.clear_reaction("<a:loading:856179279292006430>")

        await ctx.send(embed=embed)

    @commands.cooldown(1, 86400, commands.BucketType.user)
    @command(name="rep", brief="Give a reputation point to the user")
    async def reputation_command(self, ctx, member: Member):
        """Give a reputation point to the user"""
        await self.reputation_handler(ctx, member)

    async def reputation_handler(self, ctx, member):
        if member is ctx.author:
            await ctx.send("you cannot give reputation points to yourself.")
            return
        model, _ = await ReputationPoints.get_or_create(
            member_name=member.name, guild_id=ctx.guild.id
        )
        model.points = model.points + 1
        await model.save()
        embed = Embed(color=Color.green())  # timestamp=datetime.utcnow())
        embed.set_author(
            name=f"{ctx.author.name} gave a reputation point to {member.name}",
            icon_url=ctx.author.avatar_url,
        )
        await ctx.send(embed=embed)

    @command(name="replist", brief="View the leaderboard of reputation for the server.")
    async def replist_command(self, ctx):
        """View the leaderboard of reputation for the server."""
        rep_model = (
            await ReputationPoints.filter(guild_id=ctx.guild.id)
            .order_by("-points")
            .limit(10)
        )
        leaderboard = "\n".join(
            [
                f"**{i+1}.** {model.member_name} - {model.points}"
                for (i, model) in enumerate(rep_model)
            ]
        )
        # print(leaderboard)
        embed = Embed(
            description=leaderboard if len(rep_model) else "No data found",
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        embed.set_author(
            name=f"{ctx.guild.name} Reputation Leaderboard", icon_url=ctx.guild.icon_url
        )
        await ctx.send(embed=embed)

    @command(
        name="remainder",
        aliases=["remind", "remindme"],
        brief="Set a remainder for things.",
    )
    async def remainder_command(self, ctx, time: TimeConverter, *, reason):
        """Set a remainder for things."""
        timers.Timer(
            self.client, "remainder", time, args=(ctx.channel.id, ctx.author.id, reason)
        ).start()
        embed = Embed(color=Color.blurple())
        embed.set_author(
            name=f"Set a remainder for reason - {reason}",
            icon_url=ctx.author.avatar_url,
        )
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_remainder(self, channel_id, author_id, reason):
        channel = self.client.get_channel(channel_id)
        await channel.send(f" <@{author_id}>, Remainder: {reason}")


def setup(client):
    client.add_cog(Misc(client))
