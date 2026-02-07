import discord
from discord import app_commands
from discord.ext import commands
import re
import logging
from dotenv import load_dotenv
import dateparser
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = discord.Object(id=1469781030989992091)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MeetBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f"Loaded extension: {filename}")
                
        # Sync commands to your test server immediately
        self.tree.copy_global_to(guild=GUILD_ID)
        await self.tree.sync(guild=GUILD_ID)
        print("Commands synced!")

client = MeetBot()
client.run(TOKEN)