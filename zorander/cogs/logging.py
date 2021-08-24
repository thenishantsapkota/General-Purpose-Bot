from datetime import datetime
from operator import add

import discord
from discord import Embed, Member, Message
from discord.colour import Color
from discord.ext import commands
from discord.ext.commands import Cog, command

from zorander import Bot
from zorander.utils.permissions import Permissions


class Logging(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.permissions = Permissions()

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member) -> None:
        logging_channel = await self.permissions.logging_channel_check(before.guild)
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
        logging_channel = await self.permissions.logging_channel_check(
            before.author.guild
        )
        if not after.author.bot:
            if before.content != after.content:
                embed = Embed(
                    color=Color.green(),
                    description=f"Edit by `{after.author}` in {after.channel.mention}",
                    timestamp=datetime.utcnow(),
                )

                embed.set_author(name=f"Message Edited")

                fields = [
                    ("Before", before.content, False),
                    ("After", after.content, False),
                ]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await logging_channel.send(embed=embed)

    @Cog.listener()
    async def on_message_delete(self, message: Message) -> None:
        logging_channel = await self.permissions.logging_channel_check(
            message.author.guild
        )
        if not message.author.bot:
            embed = Embed(
                description=f"Action by `{message.author}` in {message.channel.mention}",
                color=Color.red(),
                timestamp=datetime.utcnow(),
            )

            embed.set_author(name=f"Message Deleted")

            embed.add_field(name="Content", value=message.content, inline=False)
            await logging_channel.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Logging(bot))
