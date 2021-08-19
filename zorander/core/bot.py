"""
This is the main file for running the Bot
"""
import logging
import os
from pathlib import Path

import discord
from aiohttp import ClientSession
from discord import Color
from discord.ext import commands, tasks
from discord.ext.commands.bot import when_mentioned_or
from discord.http import HTTPClient
from tortoise import Tortoise

from ..utils.activity import CustomActivity
from ..utils.cogload import CogsLoad
from ..utils.cogreload import CogsReload
from .models import GuildModel, OverrideModel
from .tortoise_config import tortoise_config

os.environ.setdefault("JISHAKU_HIDE", "1")
os.environ.setdefault("JISHAKU_RETAIN", "1")
os.environ.setdefault("JISHAKU_NO_UNDERSCORE", "1")

logger = logging.getLogger("zorander.main")
logging.basicConfig(level=logging.INFO)


class CommandDisabled(commands.CommandError):
    pass


class Bot(commands.Bot):
    """Custom class for creating a bot instance"""

    http: HTTPClient

    def __init__(self) -> None:
        self._cogs = [p.stem for p in Path("./zorander/cogs/").glob("*.py")]
        self.color = Color.teal()
        self.reloader = CogsReload(self)
        self.loader = CogsLoad(self)
        self.custom_activity = CustomActivity(self)
        super().__init__(
            command_prefix=self._get_prefix,
            intents=discord.Intents.all(),
        )
        self.add_check(self.checkenabled)
        self.owner_ids = [852617608309112882]

    async def _get_prefix(self, bot: commands.Bot, message: discord.Message) -> str:
        if not message.guild:
            return ">"

        data, _ = await GuildModel.get_or_create(guild_id=message.guild.id)
        prefix = data.prefix
        return when_mentioned_or(prefix)(bot, message)

    @property
    def session(self) -> ClientSession:
        return self.http._HTTPClient__session

    
    @tasks.loop(seconds=0, count=1)
    async def connect_db(self) -> None:
        logger.info("Connecting to the Database....")
        await Tortoise.init(tortoise_config)
        logger.info("Connected to DB.")

    async def on_ready(self) -> None:
        self.reloader.cog_watcher_task.start()
        logger.info("Started Cog Reloader.")
        await self.loader.cog_load()
        logger.info("Bot is ready!")

        for i in self.guilds:
            logger.info(f"Server Name: {i.name}, Members: {i.member_count}")

        self.connect_db.start()
        logger.info(f"Logged in as {self.user}")
    

    async def checkenabled(self, ctx: commands.Context) -> None:
        check = await OverrideModel.get_or_none(
            guild_id=ctx.guild.id,
            channel_id=ctx.channel.id,
            command_name=ctx.command.name,
            enable=False,
        )
        if check:
            raise CommandDisabled(message="Command Disabled in this channel")
        return True
