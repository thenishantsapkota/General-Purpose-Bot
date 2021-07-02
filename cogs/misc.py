from datetime import date
from pathlib import Path
from dotenv import load_dotenv
import aiohttp
from io import BytesIO

from modules.imports import *


load_dotenv()
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

WEATHER_TOKEN = os.getenv("WEATHER_API_TOKEN")


class Misc(Cog):
    def __init__(self, client):
        self.client = client

    @command(name="avatar", aliases=["av"], brief="Returns the member's avatar.")
    async def avatar_command(self, ctx, member: Optional[Member]):
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
        ping = int(self.client.latency * 1000)
        embed = Embed(
            title="Pong!", description=f"My ping is {ping}ms.", color=Color.green()
        )
        await ctx.send(embed=embed)

    @command(name="botinvite", brief="Returns the invite link of bot")
    async def botinvite_command(self, ctx):
        invite = f"https://discord.com/oauth2/authorize?client_id={self.client.user.id}&permissions=0&scope=bot"
        await ctx.send(invite)

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
            url=f"https://flagcdn.com/w80/{str(alpha2Code).lower()}.png"
        )
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    @command(name="githubinfo")
    async def githubinfo_command(self, ctx, *, githubusername: str):
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

    @command(name="weather")
    async def weather_command(self, ctx, *, cityName: str):
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
    
    @command(name="carbon")
    async def carbon_command(self, ctx, *, codeblock:str):
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
            #print(codes)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://carbonnowsh.herokuapp.com/?code={codes}&theme=monokai") as resp:
                    file = BytesIO(await resp.read())
                    bytes = file.getvalue()
                file = open("carbon.png", "wb")
                file.write(bytes)
                file.close()
                await ctx.send(file=discord.File(fp="carbon.png", filename="carbon.png"))
                os.remove("carbon.png")

                


def setup(client):
    client.add_cog(Misc(client))
