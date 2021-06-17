from db.db_welcome import WelcomeDB
from db.db_overrides import Overrides
from modules.imports import *
from db.db_prefix import *

class Events(Cog):

    def __init__(self, client):
        self.client = client

    @Cog.listener()
    async def on_ready(self):
        #print("Bot is Ready!")
        print(f"Logged in as  - {self.client.user.name} active in...")
        for i in self.client.guilds:
            print(f"{i.name}")
            await self.client.change_presence(activity=discord.Game(name="Visual Studio Code"))
    
    @Cog.listener()
    async def on_message(self, msg):
        if self.client.user.mentioned_in(msg):
            for prefix in session.query(BotPrefix).filter(BotPrefix.guild_id == msg.guild.id):
                embed = Embed(
                    title = "Prefix",
                    description = f"My prefix for {msg.guild.name} is `{prefix.prefix_bot}`",
                    timestamp = datetime.utcnow(),
                    color = Color.blurple()
                )
                await msg.channel.send(embed = embed)
    @Cog.listener()
    async def on_guild_join(self,guild):
        try:
            guild_info = BotPrefix(">",guild.id)
            welcomeInfo = WelcomeDB("0", guild.id,"Enjoy your stay here.")
            session.add(guild_info)
            session.add(welcomeInfo)
            session.commit()
            session.commit()
        except:
            pass
    
    @Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            session.query(BotPrefix).filter(BotPrefix.guild_id == guild.id).delete()
            session.query(WelcomeDB).filter(WelcomeDB.guild_id == guild.id).delete()
            session.commit()
            session.commit()
        except:
            pass
        


def setup(client):
    client.add_cog(Events(client))