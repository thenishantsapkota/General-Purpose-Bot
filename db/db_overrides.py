#from modules.imports import *

from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "sqlite:///D:\Python Programming\General-Bot\db\database.db")
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Overrides(Base):

    __tablename__ = "overrides"

    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer)

    def __init__(self, channel_id):
        self.channel_id = channel_id


channel_ids = []

for r in session.query(Overrides):
    channel_ids += [r.channel_id]
