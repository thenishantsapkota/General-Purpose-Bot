from modules.imports import *


engine = create_engine("sqlite:///D:\Python Programming\General-Bot\db\database.db")
Session = sessionmaker(bind=engine)
session =Session()

Base = declarative_base()

class Overrides(Base):

    __tablename__ = "overrides"

    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer)
    guild_id = Column(Integer)
    cmd = Column(String)
    bool = Column(Integer)

    def __init__(self, channel_id, guild_id, cmd, bool):
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.cmd = cmd
        self.bool = bool
