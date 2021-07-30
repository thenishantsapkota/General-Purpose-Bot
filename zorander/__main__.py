import os
from pathlib import Path

from dotenv import load_dotenv

from .core import Bot

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

if __name__ == "__main__":
    bot = Bot()
    bot.run(os.getenv("TOKEN"))
