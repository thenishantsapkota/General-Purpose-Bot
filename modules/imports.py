import discord
from discord import (
    Color,
    DMChannel,
    Embed,
    Member,
    User,
    TextChannel,
    VoiceChannel,
    Role,
)
from discord.ext import commands, tasks
from discord.utils import get
from discord.ext.commands import Cog, command, Greedy, CommandNotFound
from discord.ext.menus import MenuPages, ListPageSource
import jishaku

import os
import io
import os.path

import requests
from pathlib import Path

import random
import asyncio

from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import json
from datetime import datetime,timedelta
from typing import Optional, List
import traceback
import sys
import re
import aiohttp
