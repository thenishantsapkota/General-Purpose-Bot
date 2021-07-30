import logging
from typing import TYPE_CHECKING

import jishaku

if TYPE_CHECKING:
    from zorander import Bot

logger = logging.getLogger("zorander.cogload")


class CogsLoad:
    def __init__(self, bot: "Bot") -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        for ext in self.bot._cogs:
            self.bot.load_extension(f"zorander.cogs.{ext}")
            logger.info(f"Loaded {ext}")
        self.bot.load_extension("jishaku")
        logger.info("Loaded Jishaku.")
