from itertools import cycle
from typing import TYPE_CHECKING

import discord
from discord.ext import tasks

if TYPE_CHECKING:
    from zorander import Bot


class CustomActivity:
    def __init__(self, bot: "Bot") -> None:
        self.bot = bot
        self._statuses = cycle(
            [
                lambda: discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f">help | Use >help to get help.",
                ),
                lambda: discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"{len(self.bot.guilds)} guilds.",
                ),
                lambda: discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"Fun commands and much more.",
                ),
                lambda: discord.Activity(
                    type=discord.ActivityType.playing, name=f"Neo Vim | Coding Myself"
                ),
                lambda: discord.Activity(
                    type=discord.ActivityType.watching, name=f"{len(self.bot.commands)} commands."
                ),
            ]
        )
        self.change_presence.start()

    @tasks.loop(seconds=20)
    async def change_presence(self) -> None:
        new_presence = next(self._statuses)
        await self.bot.change_presence(
            status=discord.Status.idle, activity=new_presence()
        )

    @change_presence.before_loop
    async def before_change_status(self):
        await self.bot.wait_until_ready()
