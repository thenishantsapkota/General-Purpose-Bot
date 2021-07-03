import jishaku
import watchgod
from discord.ext import tasks
from discord.ext.commands.bot import Bot
from tortoise import Tortoise

from db.db_token import token
from models import OverrideModel, PrefixModel
from modules.imports import *
from tortoise_config import tortoise_config

TOKEN = token

intents = discord.Intents.default()
intents.members = True

os.environ.setdefault("JISHAKU_HIDE", "1")
os.environ.setdefault("JISHAKU_RETAIN", "1")
os.environ.setdefault("JISHAKU_NO_UNDERSCORE", "1")


class CommandDisabled(commands.CommandError):
    pass


async def get_prefix(client, message):
    data = await PrefixModel.get_or_none(guild_id=message.guild.id)
    prefix_ = str(data.prefix)
    return prefix_


client = commands.Bot(command_prefix=get_prefix, intents=intents)
client.owner_ids = [489345219846733824, 479886922471440385]
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")


@tasks.loop(seconds=0, count=1)
async def connect_db():
    await Tortoise.init(tortoise_config)
    print("Connected to DB.")


@client.check
async def checkenabled(ctx: commands.Context):
    check = await OverrideModel.get_or_none(
        guild_id=ctx.guild.id,
        channel_id=ctx.channel.id,
        command_name=ctx.command.name,
        enable=False,
    )
    if check:
        raise CommandDisabled(message="Command Disabled in this channel")
    return True


@tasks.loop(seconds=1)
async def cog_watcher_task() -> None:
    """Watches the cogs directory for changes and reloads files"""
    async for change in watchgod.awatch("cogs", watcher_cls=watchgod.PythonWatcher):
        for change_type, changed_file_path in change:
            try:
                extension_name = changed_file_path.replace(os.path.sep, ".")[:-3]
                if len(extension_name) > 36 and extension_name[-33] == ".":
                    continue
                if change_type == watchgod.Change.modified:
                    try:
                        client.unload_extension(extension_name)
                    except commands.ExtensionNotLoaded:
                        pass
                    finally:
                        client.load_extension(extension_name)
                        print(f"AutoReloaded {extension_name}.")
                else:
                    try:
                        client.unload_extension(extension_name)
                        print(f"AutoUnloaded {extension_name}.")
                    except commands.ExtensionNotLoaded:
                        pass
            except (commands.ExtensionFailed, commands.NoEntryPointError) as e:
                traceback.print_exception(type(e), e, e.__traceback__)


@client.event
async def on_ready():
    connect_db.start()
    cog_watcher_task.start()


client.run(TOKEN)
