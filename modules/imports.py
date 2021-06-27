import asyncio
import io
import json
import os
import os.path
import random
import re
import sys
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import aiohttp
import discord
import jishaku
import requests
from discord import (
    Color,
    DMChannel,
    Embed,
    Member,
    Role,
    TextChannel,
    User,
    VoiceChannel,
)
from discord.ext import commands, tasks
from discord.ext.commands import Cog, CommandNotFound, Greedy, command
from discord.ext.menus import ListPageSource, MenuPages
from discord.utils import get
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
