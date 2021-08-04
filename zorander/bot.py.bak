import logging
import os
from pathlib import Path

import discord
from discord import Color
from discord.ext import commands, tasks
from discord.ext.commands.bot import when_mentioned_or
from dotenv import load_dotenv
from models import GuildModel
from tortoise import Tortoise
from tortoise_config import tortoise_config

from .utils.cogload import CogsLoad
from .utils.cogreload import CogsReload

load_dotenv()

logger = logging.getLogger("zorander.main")
logging.basicConfig(level=logging.INFO)


class Bot(commands.Bot):
    """Custom class for creating a bot instance"""

    def __init__(self) -> None:
        self._cogs = [p.stem for p in Path("./zorander/cogs/").glob("*.py")]
        self.color = Color.teal()
        self.reloader = CogsReload(self)
        self.loader = CogsLoad(self)
        super().__init__(
            command_prefix=self._get_prefix,
            intents=discord.Intents.all(),
        )

    async def _get_prefix(self, bot: commands.Bot, message: discord.Message) -> str:
        if not message.guild:
            return ">"

        data, _ = await GuildModel.get_or_create(guild_id=message.guild.id)
        prefix = data.prefix
        return when_mentioned_or(prefix)(bot, message)

    @tasks.loop(seconds=0, count=1)
    async def connect_db(self):
        logger.info("Connecting to the Database....")
        await Tortoise.init(tortoise_config)
        logger.info("Connected to DB.")

    async def on_ready(self):
        self.reloader.cog_watcher_task.start()
        logger.info("Started Cog Reloader.")
        await self.loader.cog_load()
        activity = discord.Activity(
            type=discord.ActivityType.watching, name="Your Dark Future <3"
        )
        await self.change_presence(activity=activity, status=discord.Status.idle)
        logger.info("Bot is ready!")

        self.connect_db.start()
        logger.info(f"Logged in as {self.user}")
