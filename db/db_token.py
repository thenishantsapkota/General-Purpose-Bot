from modules.imports import *


engine = create_engine("sqlite:///D:\Python Programming\Bot\db\database.db")
Session = sessionmaker(bind=engine)
session =Session()

Base = declarative_base()

class BotToken(Base):

    __tablename__ = "bot_key"

    bot_token = Column(String, primary_key=True)


    def __init__(self, bot_token):
        self.bot_token = bot_token


for r in session.query(BotToken):
    token = r.bot_token