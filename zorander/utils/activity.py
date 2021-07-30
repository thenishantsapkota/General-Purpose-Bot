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
                    name=f"Your Dark Future <3",
                ),
                lambda: discord.Activity(
                    type=discord.ActivityType.listening,
                    name=f"Samrid is Baun.",
                ),
                lambda: discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"Why are you gae.",
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
