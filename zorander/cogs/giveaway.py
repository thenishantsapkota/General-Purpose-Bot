import asyncio
import re
from datetime import datetime, timedelta
from random import choice
import random
from typing import Optional, Text

import discord
from discord import Embed, Guild, Member, User, message
from discord.channel import TextChannel
from discord.ext import commands
from discord.ext.commands import Cog, command

from zorander import Bot
from zorander.utils.time import *

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> float:
        """Function that converts given time into seconds.

        Parameters
        ----------
        ctx : commands.Context
            Context of the command invokation.
        argument : str
            Time to be converted

        Returns
        -------
        float
            Time in seconds.

        Raises
        ------
        commands.BadArgument
            When the values are wrong and when the input doesn't match the input regex.
        """
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


class Giveaway(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.cancelled = False

    @commands.group(invoke_without_command=True)
    async def giveaway(self, ctx: commands.Context) -> None:
        embed = Embed(
            title="Giveaway setup Help",
            description="Setup Your giveaway in some simple commands",
            color=self.bot.color,
        )
        embed.add_field(
            name="Create Giveaway",
            value="Create a giveaway by using the `giveaway create` command. The bot will ask some simple questions to host your giveaway",
        )
        embed.add_field(
            name="Reroll Giveaway",
            value="Reroll a giveaway again by using the `giveaway reroll` command.The bot will ask some simple questions to host your giveaway",
        )
        embed.add_field(
            name="Cancel Giveaway",
            value="Delete a giveaway by using the `giveaway delete` command. The bot will ask some simple questions to host your giveaway",
        )
        await ctx.send(embed=embed)

    @giveaway.command(name="create")
    @commands.has_permissions(manage_guild=True)
    async def giveaway_create(self, ctx: commands.Context, time: TimeConverter) -> None:
        """Host a giveaway in the server."""
        embed = Embed(
            title="Setup Giveaway!! ✨",
            description="Answer the following questions in 25 seconds each for the Giveaway",
            color=self.bot.color,
        )
        await ctx.send(embed=embed)
        questions = [
            "In Which channel do you want to host the giveaway?",
            "What is the Prize?",
            "How many winners will it have?",
        ]
        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        for i, question in enumerate(questions):
            embed = Embed(title=f"Question {i+1}", description=question)
            await ctx.send(embed=embed)
            try:
                message = await self.bot.wait_for("message", timeout=25, check=check)

            except TimeoutError:
                await ctx.send("You didn't answer the questions in time.")
                return
            answers.append(message.content)
        try:
            channel_id = int(answers[0][2:-1])

        except:
            await ctx.send(
                f"The channel you provided was wrong, channel should be in this format -> {ctx.channel.mention}"
            )
            return
        channel = self.bot.get_channel(channel_id)
        prize = answers[1]
        pretty_time = pretty_timedelta(timedelta(seconds=int(time)))
        await ctx.send(
            f"Your giveaway will be hosted in {channel} and will last for {pretty_time}"
        )
        embed = Embed(
            title=f"{prize} Giveaway!",
            description=f"🎉 Winners : {answers[2]}\nEnd Time : {pretty_time}\nGiveaway Creation Time: {pretty_datetime(datetime.now())}",
            color=0x00FFFF,
        )
        embed.set_footer(text=f"Hosted By : {ctx.author}")
        newMsg = await channel.send(embed=embed)
        await newMsg.add_reaction("🎉")

        self.cancelled = False

        await asyncio.sleep(time)

        if not self.cancelled:
            myMsg = await channel.fetch_message(newMsg.id)
            users = await myMsg.reactions[0].users().flatten()
            users.pop(users.index(self.bot.user))

        if len(users) <= 0:
            empty_embed = Embed(
                title=f"{prize} Giveaway!",
                description=f"🎉 Winners : {answers[2]}",
            )
            empty_embed.add_field(name="Winner:", value=f"No one won the giveaway.")
            empty_embed.set_footer(text=f"Hosted by : {ctx.author}")
            await myMsg.edit(embed=empty_embed)
            return
        if len(users) > 0:
            winners = random.sample(users, int(answers[2]))
            winner_embed = Embed(
                title=f"{prize} Giveaway!",
                description=f"🎉 Winners : {answers[2]}",
                color=0x00FFFF,
            )
            winner = ",".join([winner.mention for winner in winners])
            winner_embed.add_field(name="Winner of the Giveaway:", value=winner)
            winner_embed.set_footer(text=f"Hosted by : {ctx.author}")
            await myMsg.edit(embed=winner_embed)
            await ctx.send(
                f"Congratulations {winner}  on winning `{prize}` Giveaway."
            )
            return
    
    @giveaway.command(name="reroll")
    async def reroll_command(self, ctx: commands.Context, channel: TextChannel, id_:int, winners: int) -> None:
        """Reroll the giveaway if found."""
        msg = await channel.fetch_message(id_)
        users = await msg.reactions[0].users().flatten()
        users.pop(users.index(self.bot.user))
        if len(users) <= 0:
            empty_embed = Embed(
                title=f"Giveaway!",
                description=f"🎉 Winners : {winners}",
            )
            empty_embed.add_field(name="Winner:", value=f"No one won the giveaway.")
            empty_embed.set_footer(text=f"Hosted by : {ctx.author}")
            await msg.edit(embed=empty_embed)
            return
        if len(users) > 0:
            winners = random.sample(users, int(winners))
            winner_embed = Embed(
                title=f"Giveaway!",
                description=f"🎉 Winners : {winners}",
                color=0x00FFFF,
            )
            winner = ",".join([winner.mention for winner in winners])
            winner_embed.add_field(name="Winner of the Giveaway:", value=winner)
            winner_embed.set_footer(text=f"Hosted by : {ctx.author}")
            await msg.edit(embed=winner_embed)
            await ctx.send(
                f"Congratulations {winner}  on winning the Giveaway."
            )
            return
    
    @giveaway.command(name="delete")
    async def giveaway_delete(self, ctx: commands.Context, channel: TextChannel, id_: int) -> None:
        """Delete the giveaway provided."""
        try:
            msg = await channel.fetch_message(id_)
            newEmbed = Embed(title="Giveaway Cancelled", description="The giveaway has been cancelled!!")
            self.cancelled = True
            await msg.edit(embed=newEmbed) 
        except:
            embed = Embed(title="Failure!", description="Cannot cancel Giveaway")
            await ctx.send(emebed=embed)



def setup(bot: Bot) -> None:
    bot.add_cog(Giveaway(bot))
