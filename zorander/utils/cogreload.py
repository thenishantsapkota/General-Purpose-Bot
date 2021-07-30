import logging
import os
import traceback
from pathlib import Path
from typing import TYPE_CHECKING

import watchgod
from discord.ext import commands, tasks

if TYPE_CHECKING:
    from zorander import Bot

logger = logging.getLogger("zorander.cogreload")


class CogsReload:
    def __init__(self, bot: "Bot"):
        self.bot = bot

    @tasks.loop(seconds=1)
    async def cog_watcher_task(self) -> None:
        """Watches the cogs directory for changes and reloads files"""
        extension_name = [p.stem for p in Path("./zorander/cogs/").glob("*.py")]
        async for change in watchgod.awatch(
            Path("./zorander/cogs/"), watcher_cls=watchgod.PythonWatcher
        ):
            for change_type, changed_file_path in change:
                try:
                    extension_name = changed_file_path.replace(os.path.sep, ".")[:-3]
                    if len(extension_name) > 36 and extension_name[-33] == ".":
                        continue
                    if change_type == watchgod.Change.modified:
                        try:
                            self.bot.unload_extension(extension_name)
                        except commands.ExtensionNotLoaded:
                            pass
                        finally:
                            self.bot.load_extension(extension_name)
                            logger.info(f"AutoReloaded {extension_name}.")
                    else:
                        try:
                            self.bot.unload_extension(extension_name)
                            logger.info(f"AutoUnloaded {extension_name}.")
                        except commands.ExtensionNotLoaded:
                            pass
                except (commands.ExtensionFailed, commands.NoEntryPointError) as e:
                    traceback.print_exception(type(e), e, e.__traceback__)
