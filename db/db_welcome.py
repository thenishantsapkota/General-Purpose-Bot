from modules.imports import *


engine = create_engine(
    "sqlite:///D:\Python Programming\General-Bot\db\database.db")
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class WelcomeDB(Base):

    __tablename__ = "welcomechannel"

    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer)
    guild_id = Column(Integer)
    welcome_message = Column(String)

    def __init__(self, channel_id, guild_id, welcome_message):
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.welcome_message = welcome_message
