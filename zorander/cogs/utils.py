import asyncio
import logging
from datetime import datetime

import discord
import pytz
from discord import Color, Embed, Role
from discord.ext import commands
from discord.ext.commands import Cog, command

from zorander import Bot
from zorander.cogs.errors import MessageNotFound
from zorander.core.models import ModerationRoles, MuteModel

from ..core.models import GuildModel


class Utils(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.message_not_referenced = MessageNotFound()

    @command(
        name="changeprefix", aliases=["chp"], brief="Change the prefix of the server."
    )
    @commands.has_permissions(administrator=True)
    async def changeprefix(self, ctx: commands.Context, prefix: str) -> None:
        """Change the prefix of the server."""
        model = await GuildModel.get_or_none(guild_id=ctx.guild.id)
        model.prefix = prefix
        await model.save()
        response = f"The prefix for {ctx.guild} has been changed to `{prefix}.`"
        await ctx.send(response)

    @command(name="hello", brief="Returns the current prefix of the server.")
    async def prefix_command(self, ctx: commands.Context) -> None:
        """Greets the user with the current prefix of the server."""
        model = await GuildModel.get_or_none(guild_id=ctx.guild.id)
        prefix = model.prefix
        response = f"Hello {ctx.author.name}, My prefix here is {self.bot.user.mention} or `{prefix}`\nUse the `{prefix}changeprefix <new_prefix>` command to change it."
        await ctx.send(response)

    @Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(5)
        models = MuteModel.all()
        async for model in models:
            asyncio.create_task(self.mute_handler(model))

    async def mute_handler(self, model: MuteModel):
        utc = pytz.UTC
        localized_mutetime = model.time
        localized_nowtime = utc.localize(datetime.now())
        if localized_mutetime > localized_nowtime:
            remaining_time = (localized_mutetime - localized_nowtime).total_seconds()
            await asyncio.sleep(remaining_time)
            await self.mute_handler_get(model)
            # print("Success")
            return
        await self.mute_handler_get(model)
        # print("Sucess - A")

    async def mute_handler_get(self, model: MuteModel):
        guild = self.client.get_guild(model.guild_id)
        member = guild.get_member(model.member_id)
        logChannel = discord.utils.get(guild.text_channels, name="mod-logs")
        role_ids = model.role_id
        roles = [guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]
        await member.edit(roles=roles)
        await model.delete()
        embed = Embed(
            description=f"**:loud_sound: Unmuted {member} [ID {member.id}]**",
            color=Color.green(),
            timestamp=datetime.utcnow(),
        )
        embed.set_author(
            name=f"{self.bot.user} [ID {self.bot.user.id}]",
            icon_url=self.bot.user.avatar_url,
        )
        embed.add_field(name="Reason", value="Mute Duration Expired.")
        embed.set_thumbnail(url=member.avatar_url)
        await logChannel.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def role(self, ctx: commands.Context):
        """Role group to set moderation roles for the server."""
        embed = Embed(
            color=self.bot.color,
            timestamp=datetime.utcnow(),
        )
        embed.add_field(
            name=f"**Arguments**",
            value=f"`admin` - Set admin role for the server.\n\n`mod` - Set mod role for the server\n\n`staff` - Set staff role for the server.\n\n`give` - Give a role to the user.\nExample: `role give <member> <role>`\n\n`take` - Take a role from the user.\nExample: `role take <member> <role>`",
        )
        embed.set_author(
            name=f"Help with role command.", icon_url=self.bot.user.avatar_url
        )
        embed.set_footer(text=f"Invoked by {ctx.author}")
        await ctx.send(embed=embed)

    @role.group(name="admin")
    @commands.has_permissions(administrator=True)
    async def adminroleset(self, ctx: commands.Context, role: Role):
        """Set admin role for the server."""
        guild = ctx.guild
        author = ctx.author

        if role in ctx.guild.roles:
            model, _ = await ModerationRoles.get_or_create(guild_id=guild.id)
            model.admin_role = role.id
            await model.save()
            embed = Embed(
                title="Admin Role",
                description=f"The admin role  for {ctx.guild.name} has been set to {role.mention}",
                timestamp=datetime.utcnow(),
                color=self.bot.color,
            )
            await ctx.send(embed=embed)

    @role.group(name="mod")
    @commands.has_permissions(administrator=True)
    async def modroleset(self, ctx: commands.Context, role: Role):
        """Set mod role for the server."""
        guild = ctx.guild
        author = ctx.author

        if role in ctx.guild.roles:
            model, _ = await ModerationRoles.get_or_create(guild_id=guild.id)
            model.mod_role = role.id
            await model.save()
            embed = Embed(
                title="Moderator Role",
                description=f"The mod role  for {ctx.guild.name} has been set to {role.mention}",
                timestamp=datetime.utcnow(),
                color=self.bot.color,
            )
            await ctx.send(embed=embed)

    @role.group(name="staff")
    @commands.has_permissions(administrator=True)
    async def staffroleset(self, ctx: commands.Context, role: Role):
        """Set staff role in server"""
        guild = ctx.guild
        author = ctx.author

        if role in ctx.guild.roles:
            model, _ = await ModerationRoles.get_or_create(guild_id=guild.id)
            model.staff_role = role.id
            await model.save()
            embed = Embed(
                title="Staff Role",
                description=f"The staff role  for {ctx.guild.name} has been set to {role.mention}",
                timestamp=datetime.utcnow(),
                color=self.bot.color,
            )
            await ctx.send(embed=embed)

    @role.group(name="list", brief="List the admin, mod and staff roles of the server")
    @commands.has_permissions(administrator=True)
    async def list_command(self, ctx: commands.Context):
        """List the admin, mod and staff roles of the server"""
        author = ctx.author
        guild = ctx.guild
        model = await ModerationRoles.get_or_none(guild_id=guild.id)
        if model is None:
            await ctx.send("No data found.")
            return
        embed = Embed(
            color=self.bot.color,
            description=f"**Admin Role** - <@&{model.admin_role}>\n\n**Mod Role** - <@&{model.mod_role}>\n\n**Staff Role** - <@&{model.staff_role}>",
            timestamp=datetime.utcnow(),
        )
        embed.set_author(name=f"Staff Roles for {guild.name}", icon_url=guild.icon_url)
        embed.set_footer(text=f"Invoked by {author}")
        await ctx.send(embed=embed)

    @command(name="re")
    async def repeat_command(self, ctx: commands.Context):
        """Reply to a message to redo the command"""
        reference = ctx.message.reference
        if not reference:
            raise self.message_not_referenced
        try:
            message = await ctx.channel.fetch_message(reference.message_id)
        except discord.NotFound:
            return await ctx.reply("Couldn't find that message")
        if message.author != ctx.author:
            return
        await self.bot.process_commands(message)


def setup(bot: Bot) -> None:
    bot.add_cog(Utils(bot))
