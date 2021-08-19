import discord
from discord import TextChannel
from discord import user
from discord.ext import commands
from discord.ext.commands import Cog, command, Greedy

from zorander import Bot
from zorander.core.models import OverrideModel

from typing import Optional


class CommandOverrides(Cog):
    def __init__(self, bot : Bot) -> None:
        self.bot = bot
    
    @commands.group()
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def toggle(self, ctx: commands.Context) -> None:
        """Enable or Disable commands in a Guild Channel"""
        pass

    
    async def toggle_handler(self, ctx: commands.Context, usercommand: str, channels: list[TextChannel], toggle: bool) -> None:
        """
        Function that handles commands being enabled or disabled

        Parameters
        ----------
        ctx : commands.Context
            Context of the command invokation.
        usercommand : str
            Command that needs to be toggled on or off.
        channels : list[TextChannel]
            List of channels in which command needs to be toggled.
        toggle : bool
            Boolean value to represent whether command is enabled or disabled.
        """
        command = self.bot.get_command(usercommand)
        if not command:
            await ctx.send(f"`{usercommand}` is not a valid command.")
        if command == ctx.command:
            await ctx.send(f"You cannot disable this command.")

        else:
            for channel in channels:
                model, _ = await OverrideModel.get_or_create(
                    guild_id=ctx.guild.id,
                    command_name=command.name,
                    channel_id=channel.id,
                )
                model.enable = toggle
                await model.save()
            toggle_string = "enabled" if toggle else "disabled"
            channel_mention = "".join([channel.mention for channel in channels])
            await ctx.send(f"`{command.name}` {toggle_string} in {channel_mention}")
    
    @toggle.group(name="enable")
    async def toggle_enable(self, ctx: commands.Context, command: str, channels: Greedy[TextChannel]) -> None:
        """Enable a command in a guild channel."""
        await self.toggle_handler(ctx, command, channels, True)

    @toggle.group(name="disable")
    async def toggle_disable(self, ctx: commands.Context, command: str, channels: Greedy[TextChannel]) -> None:
        """Disable a command in a guild channel."""
        await self.toggle_handler(ctx, command, channels, False)

    @toggle.command(name="all")
    async def toggleall(self, ctx: commands.Context, command: str, toggle: bool) -> None:
        """Disable a command in all the guild channels."""
        command = self.bot.get_command(command)
        if not command:
            await ctx.send(f"`{command}` is not a valid command.")
        if command == ctx.command:
            await ctx.send(f"You cannot disable this command.")

        else:
            for channel in ctx.guild.text_channels:
                model, _ = await OverrideModel.get_or_create(
                    guild_id=ctx.guild.id,
                    command_name=command.name,
                    channel_id=channel.id,
                )
                model.enable = toggle
                await model.save()
            toggle_string = "enabled" if toggle else "disabled"
            await ctx.send(f"`{command.name}` {toggle_string} in all channels")

    @command()
    async def check(self, ctx: commands.Context, command: str, channel: Optional[TextChannel]) -> None:
        """Check if command is disabled in a certain channel."""
        command = self.bot.get_command(command)
        channel = channel or ctx.channel
        check = await OverrideModel.get_or_none(
            guild_id=ctx.guild.id, command_name=command.name, channel_id=channel.id
        )
        try:
            toggle_str = "enabled" if check.enable else "disabled"
            await ctx.send(
                f"`{command.name}` has been {toggle_str} in {channel.mention}"
            )
        except AttributeError:
            await ctx.send(f"No data of the command in the database.")

def setup(bot: Bot) -> None:
    bot.add_cog(CommandOverrides(bot))