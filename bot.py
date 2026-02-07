import discord
from discord import app_commands
from discord.ext import commands
import logging
from dotenv import load_dotenv
import dateparser
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = discord.Object(id=1469781030989992091)