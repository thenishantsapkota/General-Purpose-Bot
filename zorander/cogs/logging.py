from datetime import date, datetime
from logging import log
from operator import add

import discord
from discord import Embed, Member, Message
from discord.abc import GuildChannel
from discord.colour import Color
from discord.ext import commands
from discord.ext.commands import Cog
from discord.member import VoiceState

from zorander import Bot
from zorander.utils.permissions import Permissions


class Logging(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.permissions = Permissions()

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member) -> None:
        if not await self.bot.check_logging_disable(before.guild.id):
            return
        logging_channel = await self.permissions.member_logging_check(before.guild)
        if before.name != after.name:
            embed = Embed(
                color=after.color,
                timestamp=datetime.utcnow(),
            )

            embed.set_author(
                name=f"Username Changed - {before}", icon_url=before.avatar_url
            )

            fields = [("Before", before.name, False), ("After", after.name, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await logging_channel.send(embed=embed)

        if before.discriminator != after.discriminator:
            embed = Embed(
                color=after.color,
                timestamp=datetime.utcnow(),
            )

            embed.set_author(
                name=f"Discriminator Changed - {before}", icon_url=before.avatar_url
            )
            fields = [
                ("Before", before.discriminator, False),
                ("After", after.discriminator, False),
            ]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await logging_channel.send(embed=embed)

        if before.avatar_url != after.avatar_url:
            embed = Embed(
                description="New image is below, old to the right!",
                color=after.color,
                timestamp=datetime.utcnow(),
            )

            embed.set_author(
                name=f"Avatar Changed - {before}", icon_url=before.avatar_url
            )

            embed.set_thumbnail(url=before.avatar_url)
            embed.set_image(url=after.avatar_url)

            await logging_channel.send(embed=embed)

        if before.nick != after.nick:
            embed = Embed(
                color=after.color,
                timestamp=datetime.utcnow(),
            )

            embed.set_author(
                name=f"Nickname Changed - {before}", icon_url=before.avatar_url
            )
            fields = [("Before", before.nick, False), ("After", after.nick, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await logging_channel.send(embed=embed)

        if before.roles != after.roles:
            embed = Embed(color=after.color, timestamp=datetime.utcnow())

            embed.set_author(
                name=f"Roles Updated - {before}", icon_url=before.avatar_url
            )

            added_role = list(
                set([r.mention for r in before.roles[1:]])
                - set(r.mention for r in after.roles[1:])
            )
            removed_role = list(
                set([r.mention for r in after.roles[1:]])
                - set(r.mention for r in before.roles[1:])
            )

            fields = [
                ("Before", ", ".join([r.mention for r in before.roles[1:]]), False),
                ("After", ", ".join([r.mention for r in after.roles[1:]]), False),
                (
                    f"{'Added' if not added_role else 'Removed'} Role",
                    ", ".join(added_role if added_role else removed_role),
                    False,
                ),
            ]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await logging_channel.send(embed=embed)

    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message) -> None:
        if not await self.bot.check_logging_disable(before.author.guild.id):
            return
        logging_channel = await self.permissions.message_logs_check(before.author.guild)
        if not after.author.bot:
            if before.content != after.content:
                embed = Embed(
                    color=Color.green(),
                    description=f"Edit by `{after.author}` in {after.channel.mention}",
                    timestamp=datetime.utcnow(),
                )

                embed.set_author(
                    name=f"Message Edited", icon_url=before.author.avatar_url
                )

                fields = [
                    ("Before", before.content, False),
                    ("After", after.content, False),
                ]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await logging_channel.send(embed=embed)

    @Cog.listener()
    async def on_message_delete(self, message: Message) -> None:
        if not await self.bot.check_logging_disable(message.guild.id):
            return
        logging_channel = await self.permissions.message_logs_check(
            message.author.guild
        )
        if not message.author.bot:
            embed = Embed(
                description=f"Action by `{message.author}` in {message.channel.mention}",
                color=Color.red(),
                timestamp=datetime.utcnow(),
            )

            embed.set_author(
                name=f"Message Deleted", icon_url=message.author.avatar_url
            )

            embed.add_field(name="Content", value=message.content, inline=False)
            await logging_channel.send(embed=embed)

    @Cog.listener()
    async def on_voice_state_update(
        self, member: Member, before: VoiceState, after: VoiceState
    ) -> None:
        if not await self.bot.check_logging_disable(member.guild.id):
            return
        logging_channel = await self.permissions.voice_logs_check(member.guild)
        if before.channel is None and after.channel is not None:
            embed = Embed(
                color=Color.green(),
                description=f"**{member}** has joined in **{after.channel.name}**",
                timestamp=datetime.utcnow(),
            )

            embed.set_author(name=f"Voice Logging", icon_url=member.avatar_url)

            await logging_channel.send(embed=embed)

        if before.channel is not None and after.channel is None:
            embed = Embed(
                color=Color.red(),
                description=f"**{member}** has left **{before.channel.name}**",
                timestamp=datetime.utcnow(),
            )

            embed.set_author(name=f"Voice Logging", icon_url=member.avatar_url)

            await logging_channel.send(embed=embed)

    @Cog.listener()
    async def on_guild_channel_update(
        self, before: GuildChannel, after: GuildChannel
    ) -> None:
        if not await self.bot.check_logging_disable(before.guild.id):
            return
        logging_channel = await self.permissions.logging_channel_check(before.guild)
        if before.name != after.name:
            embed = Embed(color=Color.green(), timestamp=datetime.utcnow())

            embed.set_author(name="Channel Name Update")

            fields = [
                ("Name (Before)", before.name, False),
                ("Name (After)", after.name, False),
            ]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await logging_channel.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Logging(bot))
