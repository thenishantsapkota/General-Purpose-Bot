from modules.imports import *
from discord.ext import timers


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


class Remainders(Cog):
    def __init__(self, client):
        self.client = client

    @command(
        name="remainder",
        aliases=["remind", "remindme"],
        brief="Set a remainder for things.",
    )
    async def remainder_command(self, ctx, time: TimeConverter, *, reason):
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
    client.add_cog(Remainders(client))
