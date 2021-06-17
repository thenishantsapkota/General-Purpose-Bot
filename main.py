from discord.ext.commands.bot import Bot
from modules.imports import *
from db.db_token import token
from db.db_prefix import *

TOKEN = token

intents = discord.Intents.default()
intents.members = True


def get_prefix(client, message):
    for prefix in session.query(BotPrefix).filter(BotPrefix.guild_id == message.guild.id):
        prefixes = prefix.prefix_bot
        return(prefixes)
        break
    prefixes = ">"
    return(prefixes)


client = commands.Bot(command_prefix=get_prefix, intents=intents)
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(TOKEN)
