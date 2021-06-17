from modules.imports import *


engine = create_engine("sqlite:///D:\Python Programming\General-Bot\db\database.db")
Session = sessionmaker(bind=engine)
session =Session()

Base = declarative_base()

class BotPrefix(Base):

    __tablename__ = "prefix"

    prefix_bot =  Column(String, primary_key=True)
    guild_id = Column(String)


    def __init__(self, prefix_bot, guild_id):
        self.prefix_bot = prefix_bot
        self.guild_id = guild_id

